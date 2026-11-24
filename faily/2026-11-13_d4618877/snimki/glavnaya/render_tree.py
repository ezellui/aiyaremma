"""Сборка «фрактальной» раскладки (как в переводе 2023 г.) для любого текста «Трактата».

Вход — нормализованный JSON издания:
  title, note, front{dedication, motto, preface_title, preface[], comment[]},
  props{num: markdown}, comments[{after:[num..], text}] (необязательно),
  footnotes{label: markdown}, missing_label
Выход — Markdown и JSON с деревом.
"""
import json, re, sys
import tlp_tree


def numfmt(n):
    return (n + ".").replace(".", "\\.", 1) if "." not in n else n + "."


def paras(text):
    return [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()] if text else []


def split_blocks(text):
    """Абзацы, не разрывая блоки ```...```."""
    out, buf, inpre = [], [], False
    for chunk in text.strip().split("\n\n"):
        if inpre:
            buf.append(chunk)
            if chunk.rstrip().endswith("```"):
                out.append("\n\n".join(buf)); buf = []; inpre = False
            continue
        if chunk.lstrip().startswith("```") and not (chunk.rstrip().endswith("```") and chunk.strip() != "```" and chunk.count("```") >= 2):
            inpre = True; buf = [chunk]
            continue
        if chunk.strip():
            out.append(chunk)
    if buf:
        out.append("\n\n".join(buf))
    return out


def bold(p):
    if p.lstrip().startswith("```"):
        return p
    p = p.strip()
    return f"**{p}**"


def member_md(n, text, missing):
    if text is None:
        return f"{numfmt(n)} *[{missing}]*"
    ps = split_blocks(text)
    first = ps[0] if ps else ""
    if first.startswith("```"):
        return f"{numfmt(n)}\n\n" + "\n\n".join(ps)
    return "\n\n".join([f"{numfmt(n)} {first}"] + ps[1:])


def repeat_md(n, text, missing):
    if text is None:
        return f"**{n}.** *[{missing}]*"
    ps = split_blocks(text)
    first = ps[0] if ps else ""
    if first.startswith("```"):
        return f"**{n}.**\n\n" + "\n\n".join(bold(p) for p in ps)
    return "\n\n".join([bold(f"{n}. {first}")] + [bold(p) for p in ps[1:]])


def quote(md):
    return "\n".join(("> " + ln) if ln.strip() else ">" for ln in md.split("\n"))


def rng(nums):
    return nums[0] if len(nums) == 1 else f"{nums[0]}–{nums[-1]}"


def render(src, canon_nums):
    props = src["props"]
    missing = src.get("missing_label", "в этом издании отсутствует")
    # комментарии: к последнему положению своей «пачки»
    comm_at = {}
    for c in src.get("comments", []):
        comm_at.setdefault(c["after"][-1], []).append(c)

    out = [f"# {src['title']}", "", quote(src["note"]), ""]
    fr = src.get("front", {})
    if fr.get("dedication"):
        out += [fr["dedication"], ""]
    if fr.get("motto"):
        out += [quote(fr["motto"].replace("\n", "  \n")), ""]
    if fr.get("preface"):
        out += [f"## {fr.get('preface_title', 'Предисловие')}", ""]
        for p in fr["preface"]:
            out += [p, ""]
    if fr.get("comment"):
        out += [quote("\n\n".join([f"**{src.get('comment_label', 'Комментарий')}**"] + fr["comment"])), ""]

    def comments_after(n):
        res = []
        for c in comm_at.get(n, []):
            head = f"**{src.get('comment_label', 'Комментарий')}"
            head += f" к {rng(c['after'])}**" if len(c["after"]) > 1 else "**"
            res += [quote(head + "\n\n" + c["text"]), ""]
        return res

    for ev in tlp_tree.layout(canon_nums):
        if ev[0] == "root":
            out += ["## 1–7", ""]
            for n in ev[1]:
                out += [member_md(n, props.get(n), missing), ""]
                out += comments_after(n)
        elif ev[0] == "section":
            n = ev[1]
            ps = split_blocks(props.get(n) or f"*[{missing}]*")
            out += ["", f"## {n}. {ps[0]}" if not ps[0].startswith("```") else f"## {n}.", ""]
            out += [bold(p) for p in ps[1:]] + ([""] if ps[1:] else [])
        else:
            _, n, group, rep = ev
            if rep:
                out += ["", repeat_md(n, props.get(n), missing), ""]
            for m in group:
                out += [member_md(m, props.get(m), missing), ""]
                out += comments_after(m)

    fns = src.get("footnotes", {})
    used = []
    body = "\n".join(out)
    for m in re.finditer(r"\[\^([^\]]+)\]", body):
        if m.group(1) not in used:
            used.append(m.group(1))
    if used:
        out += ["", "---", "", f"## {src.get('notes_title', 'Примечания')}", ""]
        for lab in used:
            t = fns.get(lab)
            if t is None:
                continue
            ps = split_blocks(t)
            out.append(f"[^{lab}]: {ps[0]}")
            for p in ps[1:]:
                out.append("")
                out.append("\n".join("    " + ln for ln in p.split("\n")))
            out.append("")
    md = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    return md


def tree_json(src, canon_nums):
    nums, groups = tlp_tree.build(canon_nums)
    comm = {}
    for c in src.get("comments", []):
        comm.setdefault(c["after"][-1], []).append({"covers": c["after"], "text": c["text"]})
    nodes = []
    for n in nums:
        nodes.append({
            "num": n, "parent": tlp_tree.parent(n),
            "child_groups": groups.get(n, []),
            "text": src["props"].get(n),
            **({"comments": comm[n]} if n in comm else {}),
        })
    return {"title": src["title"], "note": src["note"], "front": src.get("front", {}),
            "nodes": nodes, "layout": tlp_tree.layout(canon_nums),
            "footnotes": src.get("footnotes", {})}


if __name__ == "__main__":
    src = json.load(open(sys.argv[1]))
    canon = json.load(open(sys.argv[2]))
    md = render(src, canon)
    open(sys.argv[3], "w").write(md)
    json.dump(tree_json(src, canon), open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
    print(sys.argv[3], len(md))
