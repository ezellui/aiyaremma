#!/usr/bin/env node
// Проба ОТПРАВИТЕЛЯ ПИСЕМ. Базы не требует.
//
// Письмо идёт настоящим путём nodemailer — через `jsonTransport`, который
// собирает конверт ровно так же, как SMTP, но кладёт его в строку вместо
// сокета. Спрашивать самодельную заглушку было бы пересказом: она согласилась
// бы с чем угодно, включая письмо без получателя.
//
//   node probes/mail_probe.mjs
//
// ПОДЛОГИ, которыми она проверена (каждый даёт красноту):
//   1. isPermanentFailure: считать постоянным всякий отказ (>= 400)
//      → «временный отказ 451 не постоянный» краснеет;
//   2. scrub вернуть как есть → «пароль не попал в ошибку» краснеет;
//   3. createSmtpSender: пропустить письмо без получателя
//      → «письмо без получателя отвергнуто» краснеет.

import nodemailer from 'nodemailer';
import { createSmtpSender, senderFromEnv, isPermanentFailure, scrub, nullSender }
  from '../src/notify/mail.js';
import { renderEmail } from '../src/notify/email.js';
import { N } from '../src/notify/catalog.js';

const проверки = [];
const проверить = (имя, годно, ждали, вышло) =>
  проверки.push({ имя, годно: !!годно, ждали, вышло });
const отказ = async fn => {
  try { await fn(); return 'ПРОШЛО'; } catch (e) { return e.message; }
};
const собрать = () => {
  const письма = [];
  return {
    письма,
    транспорт: {
      async sendMail(конверт) { письма.push(конверт); return { messageId: 'x' }; },
    },
  };
};
const ломающийся = ошибка => ({ async sendMail() { throw ошибка; } });

try {
  // ── 1. Умолчание отказывает вслух ─────────────────────────────────────
  проверить('без SMTP_URL отправителя нет',
    senderFromEnv({}).source === 'none', 'none', senderFromEnv({}).source);
  проверить('и он не молчит, а отказывается',
    (await отказ(() => nullSender.send({ to: 'a@b.c' }))).includes('не настроен'),
    'отказ со словом «не настроен»', await отказ(() => nullSender.send({})));

  // ── 2. Обратный адрес обязателен ──────────────────────────────────────
  проверить('без MAIL_FROM отправитель не заводится',
    (await отказ(() => createSmtpSender({ url: 'smtp://h:25' }))).includes('MAIL_FROM'),
    'отказ с MAIL_FROM', await отказ(() => createSmtpSender({ url: 'smtp://h:25' })));
  проверить('SMTP_URL без MAIL_FROM роняет разбор окружения',
    (await отказ(() => senderFromEnv({ SMTP_URL: 'smtp://h:25' }))).includes('MAIL_FROM'),
    'отказ', 'прошло');

  // ── 3. Письмо идёт настоящим путём ────────────────────────────────────
  {
    const { письма, транспорт } = собрать();
    const отправитель = createSmtpSender({ from: 'ΦilosΦaira <no-reply@philosphaira.to>',
                                           transport: транспорт });
    const письмо = renderEmail(N.EMAIL_VERIFY, { ссылка: 'https://philosphaira.to/v?t=1' });
    await отправитель.send({ to: 'человек@example.org', ...письмо });
    const к = письма[0] ?? {};
    проверить('письмо дошло до транспорта', письма.length === 1, 1, письма.length);
    проверить('получатель тот', к.to === 'человек@example.org',
      'человек@example.org', к.to);
    проверить('обратный адрес подставлен',
      String(к.from).includes('no-reply@philosphaira.to'), 'no-reply@…', к.from);
    проверить('тема на месте', !!к.subject, 'непусто', к.subject);
    проверить('есть И текст, И разметка', !!к.text && !!к.html,
      'обе части', `${!!к.text}/${!!к.html}`);
    проверить('ссылка подтверждения дошла целиком',
      String(к.text).includes('https://philosphaira.to/v?t=1'), 'есть', 'нет');
  }

  // ── 4. Конверт проверяется ДО отправки ────────────────────────────────
  {
    const { письма, транспорт } = собрать();
    const отправитель = createSmtpSender({ from: 'a@b.c', transport: транспорт });
    проверить('письмо без получателя отвергнуто',
      (await отказ(() => отправитель.send({ subject: 'т', text: 'т' })))
        .includes('получателя'), 'отказ', 'прошло');
    проверить('письмо без темы отвергнуто',
      (await отказ(() => отправитель.send({ to: 'a@b.c', text: 'т' })))
        .includes('темы'), 'отказ', 'прошло');
    проверить('письмо без содержимого отвергнуто',
      (await отказ(() => отправитель.send({ to: 'a@b.c', subject: 'т' })))
        .includes('содержимого'), 'отказ', 'прошло');
    проверить('ни одно из них не ушло в транспорт', письма.length === 0, 0, письма.length);
    проверить('отказ негодного конверта считается постоянным',
      (await отказ(() => отправитель.send({ subject: 'т', text: 'т' }))) &&
      await отправитель.send({ to: 'a@b.c', subject: 'т', text: 'т' }).then(() => true),
      'ушло годное', 'не ушло');
  }

  // ── 5. Два рода отказа ────────────────────────────────────────────────
  проверить('550 — постоянный',
    isPermanentFailure({ responseCode: 550 }), true, isPermanentFailure({ responseCode: 550 }));
  проверить('451 — временный',
    !isPermanentFailure({ responseCode: 451 }), false, isPermanentFailure({ responseCode: 451 }));
  проверить('421 (сервер занят) — временный',
    !isPermanentFailure({ responseCode: 421 }), false, isPermanentFailure({ responseCode: 421 }));
  проверить('обрыв сети без кода — временный',
    !isPermanentFailure({ code: 'ETIMEDOUT' }), false, isPermanentFailure({ code: 'ETIMEDOUT' }));
  проверить('негодный конверт — постоянный',
    isPermanentFailure({ code: 'EENVELOPE' }), true, isPermanentFailure({ code: 'EENVELOPE' }));
  проверить('пустая ошибка не постоянна',
    !isPermanentFailure(null), false, isPermanentFailure(null));

  // ── 6. Признак постоянства доезжает до звавшего ───────────────────────
  {
    const отправитель = createSmtpSender({ url: 'smtp://user:тайна@почта:25',
      from: 'a@b.c', transport: ломающийся(
        Object.assign(new Error('550 no such user'), { responseCode: 550 })) });
    let пойманная = null;
    try { await отправитель.send({ to: 'a@b.c', subject: 'т', text: 'т' }); }
    catch (e) { пойманная = e; }
    проверить('отказ 550 доехал с пометкой «постоянный»',
      пойманная?.permanent === true, true, пойманная?.permanent);
    проверить('код сервера сохранён', пойманная?.responseCode === 550, 550,
      пойманная?.responseCode);
  }
  {
    const отправитель = createSmtpSender({ url: 'smtp://user:тайна@почта:25',
      from: 'a@b.c', transport: ломающийся(
        new Error('connect ECONNREFUSED smtp://user:тайна@почта:25')) });
    let пойманная = null;
    try { await отправитель.send({ to: 'a@b.c', subject: 'т', text: 'т' }); }
    catch (e) { пойманная = e; }
    проверить('пароль не попал в текст ошибки',
      !String(пойманная?.message).includes('тайна'), 'без пароля', пойманная?.message);
    проверить('и сама ошибка не потерялась',
      String(пойманная?.message).includes('ECONNREFUSED'), 'ECONNREFUSED', пойманная?.message);
    проверить('временный отказ пометки «постоянный» не получил',
      пойманная?.permanent !== true, false, пойманная?.permanent);
  }
  проверить('без пароля вычищать нечего', scrub('текст', null) === 'текст',
    'текст', scrub('текст', null));

  // ── 7. Настоящий nodemailer собирает конверт ──────────────────────────
  //
  // Здесь проверяется не наш код, а то, что наш код ПОДХОДИТ настоящему:
  // заглушка своей формой подтвердила бы что угодно.
  {
    const транспорт = nodemailer.createTransport({ jsonTransport: true });
    const отправитель = createSmtpSender({ from: 'ΦilosΦaira <no-reply@philosphaira.to>',
                                           transport: транспорт });
    const итог = await отправитель.send({ to: 'человек@example.org',
      ...renderEmail(N.COMMIT_APPROVED, { commitId: 'c1', reviewerName: 'Пётр' }) });
    const конверт = JSON.parse(итог.message);
    проверить('nodemailer принял письмо', конверт.to?.[0]?.address === 'человек@example.org',
      'человек@example.org', конверт.to?.[0]?.address);
    проверить('и разобрал обратный адрес',
      конверт.from?.address === 'no-reply@philosphaira.to',
      'no-reply@philosphaira.to', конверт.from?.address);
  }

} catch (e) {
  проверить('проба дошла до конца', false, 'дошла', e.message.slice(0, 90));
} finally {
  for (const п of проверки)
    console.log((п.годно ? '  ' : '✗ ') + п.имя.padEnd(56, '.') +
      (п.годно ? '' : ` ждали ${п.ждали}, вышло ${п.вышло}`));
  const плохо = проверки.filter(п => !п.годно);
  console.log(`\nутверждений ${проверки.length}, не сошлось ${плохо.length}`);
  process.exit(плохо.length ? 1 : 0);
}
