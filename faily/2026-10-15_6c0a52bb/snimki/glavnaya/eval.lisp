;;;; src/ir/eval.lisp — интерпретатор IR и печать в виде let*.
;;;;
;;;; Интерпретатор — эталон для кодогенерации (архитектура, «Эталонный
;;;; интерпретатор»): исполняет граф обобщённой арифметикой. Вычислитель
;;;; собирается один раз для набора корней — узлы, достижимые из корней, по
;;;; возрастанию номеров, то есть в топологическом порядке, — и затем
;;;; выполняется для любых значений переменных.

(in-package #:worm.ir)

(defstruct (evaluator (:copier nil))
  (nodes #() :type simple-vector)     ; достижимые узлы по возрастанию номеров
  (roots #() :type simple-vector)     ; позиции корней в NODES
  (values nil :type (simple-array double-float (*))))

(defun reachable (roots)
  (let ((seen (make-hash-table)) (out '()))
    (labels ((walk (n)
               (unless (gethash (node-id n) seen)
                 (setf (gethash (node-id n) seen) t)
                 (loop for a across (node-args n) do (walk a))
                 (push n out))))
      (mapc #'walk roots))
    (sort out #'< :key #'node-id)))

(defun compile-evaluator (roots)
  (let* ((roots (mapcar #'ensure-node roots))
         (nodes (coerce (reachable roots) 'simple-vector))
         (pos (make-hash-table)))
    (loop for n across nodes for i from 0 do (setf (gethash (node-id n) pos) i))
    (make-evaluator :nodes nodes
                    :roots (map 'simple-vector (lambda (r) (gethash (node-id r) pos)) roots)
                    :values (make-array (length nodes) :element-type 'double-float))))

(defun evaluator-positions (ev)
  (let ((pos (make-hash-table)))
    (loop for n across (evaluator-nodes ev) for i from 0 do (setf (gethash (node-id n) pos) i))
    pos))

(defun run-evaluator (ev env)
  "Вычислить корни; ENV — функция от ключа переменной к числу. Значения
корней — списком."
  (let* ((nodes (evaluator-nodes ev))
         (vals (evaluator-values ev))
         (pos (evaluator-positions ev)))
    (flet ((arg (n k) (aref vals (gethash (node-id (aref (node-args n) k)) pos))))
      (loop for n across nodes for i from 0
            do (setf (aref vals i)
                     (float
                      (ecase (node-op n)
                        (:const (node-data n))
                        (:var (funcall env (node-data n)))
                        (:+ (loop for k below (length (node-args n)) sum (arg n k)))
                        (:* (let ((p 1d0)) (dotimes (k (length (node-args n)) p) (setf p (* p (arg n k))))))
                        (:/ (/ (arg n 0) (arg n 1)))
                        (:expt (expt (arg n 0) (node-data n)))
                        (:sqrt (let ((x (arg n 0)))
                                 (if (minusp x)
                                     (error 'floating-point-invalid-operation :operation 'sqrt :operands (list x))
                                     (sqrt x))))
                        (:exp (exp (arg n 0)))
                        (:log (let ((x (arg n 0)))
                                (if (plusp x) (log x)
                                    (error 'floating-point-invalid-operation :operation 'log :operands (list x)))))
                        (:tanh (tanh (arg n 0)))
                        (:step (if (> (arg n 0) 0d0) 1d0 0d0))
                        (:prim (apply (primitive-value (find-primitive (car (node-data n))))
                                      (append (cdr (node-data n))
                                              (loop for k below (length (node-args n)) collect (arg n k))))))
                      0d0))))
    (map 'list (lambda (i) (aref vals i)) (evaluator-roots ev))))

(defun evaluate (roots env)
  "Значение узла (или списка узлов) при значениях переменных из ENV:
функции, хэш-таблицы или списка ((ключ . значение) …)."
  (let ((fn (etypecase env
              (function env)
              (hash-table (lambda (k) (multiple-value-bind (v found) (gethash k env)
                                        (if found v (error 'ir-type-error :message (format nil "переменная ~S не задана" k))))))
              (list (lambda (k) (let ((cell (assoc k env :test #'equal)))
                                  (if cell (cdr cell) (error 'ir-type-error :message (format nil "переменная ~S не задана" k))))))))
        (single (node-p roots)))
    (let ((vals (run-evaluator (compile-evaluator (if single (list roots) roots)) fn)))
      (if single (first vals) vals))))

(defun let-form (roots &key (var-name (lambda (key) key)))
  "Корни как (let* ((vN …) …) (values …)): общие подвыражения названы
один раз, порядок — по номерам узлов. VAR-NAME превращает ключ переменной
в форму её чтения."
  (let* ((roots (mapcar #'ensure-node roots))
         (nodes (reachable roots))
         (names (make-hash-table)))
    (flet ((ref (n)
             (cond ((const-p n) (const-value n))
                   ((var-p n) (funcall var-name (var-key n)))
                   (t (gethash (node-id n) names)))))
      (let ((bindings
              (loop for n in nodes
                    unless (or (const-p n) (var-p n))
                      collect (let ((sym (intern (format nil "V~D" (node-id n)) :worm.ir))
                                    (args (map 'list #'ref (node-args n))))
                                (setf (gethash (node-id n) names) sym)
                                (list sym
                                      (case (node-op n)
                                        (:expt (list 'expt (first args) (node-data n)))
                                        (:step (list 'step (first args)))
                                        (:prim (list* (car (node-data n)) (append (cdr (node-data n)) args)))
                                        (t (cons (intern (symbol-name (node-op n)) :worm.ir) args))))))))
        `(let* ,bindings (values ,@(mapcar #'ref roots)))))))
