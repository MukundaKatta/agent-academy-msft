"""Build the agent-academy-msft demo video end-to-end."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
FG = "#0f172a"
FG_MUTED = "#475569"
ACCENT = "#5b21b6"   # violet-800 (Semantic Kernel-ish)
ACCENT_2 = "#16a34a"
ACCENT_3 = "#dc2626"
BG = "#ffffff"
PANEL = "#f8fafc"
CODE_BG = "#0f172a"
CODE_FG = "#e2e8f0"

SF = "/System/Library/Fonts/SFNS.ttf"
SFI = "/System/Library/Fonts/SFNSItalic.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(MONO).exists():
    MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False, italic=False):
    path = MONO if mono else (SFI if italic else SF)
    return ImageFont.truetype(path, size)


@dataclass
class Slide:
    name: str
    narration: str
    draw: callable


def base(img, d, title=None, eyebrow=None):
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "agent-academy-msft", font=font(22), fill=FG)
    d.text((W - 640, H - 44), "github.com/MukundaKatta/agent-academy-msft", font=font(22), fill=FG_MUTED)
    if eyebrow:
        d.text((96, 80), eyebrow.upper(), font=font(26), fill=ACCENT)
    if title:
        d.text((96, 130), title, font=font(72), fill=FG)
        d.rectangle([(96, 230), (220, 236)], fill=ACCENT)


def draw_title(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "github.com/MukundaKatta/agent-academy-msft", font=font(22), fill=FG_MUTED)
    d.text((W - 270, H - 44), "Apache 2.0", font=font(22), fill=FG_MUTED)
    d.text((96, 300), "agent-academy-msft", font=font(110), fill=FG)
    d.rectangle([(96, 450), (340, 460)], fill=ACCENT)
    d.text((96, 500), "A pull-request reviewer agent on", font=font(48), fill=FG_MUTED)
    d.text((96, 560), "Microsoft Semantic Kernel + Gemini.", font=font(48), fill=FG_MUTED)
    d.text((96, 740), "Agent Academy hackathon, Microsoft track.", font=font(32), fill=FG)


def draw_problem(img, d):
    base(img, d, title="The setup", eyebrow="Why this agent")
    rows = [
        "Every Friday afternoon someone opens a 1,800-line PR",
        "that touches src/auth and asks for a fast review.",
        "The reviewer needs to figure out:",
        "  is this risky, is there enough test coverage,",
        "  does it touch security boundaries, can I approve.",
        "",
        "The agent does the first pass in seven seconds.",
    ]
    y = 320
    for line in rows:
        d.text((96, y), line, font=font(36), fill=FG if line and not line.startswith("  ") else FG_MUTED)
        y += 60


def draw_microsoft(img, d):
    base(img, d, title="The Microsoft product", eyebrow="What we built on")
    d.text((96, 320), "Microsoft Semantic Kernel", font=font(60), fill=ACCENT)
    d.text((96, 410), "Microsoft's open-source agent SDK.", font=font(38), fill=FG_MUTED)
    d.text((96, 470), "Kernel + kernel_function + FunctionChoiceBehavior.", font=font(32, mono=True), fill=FG)
    d.text((96, 580), "Provider-agnostic. This build routes through Vertex AI", font=font(32), fill=FG)
    d.text((96, 625), "Gemini 2.5 Flash via SK's VertexAIChatCompletion.", font=font(32), fill=FG)
    d.text((96, 720), "Swap AzureChatCompletion in five lines if you have Azure.", font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 770), "That's the point: the agent shape is portable across LLMs.", font=font(28, italic=True), fill=FG_MUTED)


def draw_architecture(img, d):
    base(img, d, title="How it works", eyebrow="Architecture")
    box_w = 380
    boxes = [
        ("Repo + PR number", "openclaw/openclaw#24800", ACCENT),
        ("SK Kernel + Gemini", "VertexAIChatCompletion", FG),
        ("GitHubPRPlugin", "3 kernel_function tools", ACCENT_2),
    ]
    x = (W - 3 * box_w - 100) // 2
    for label, sub, color in boxes:
        d.rounded_rectangle([(x, 360), (x + box_w, 490)], radius=14, outline=color, width=4, fill=BG)
        d.text((x + 24, 380), label, font=font(30), fill=FG)
        d.text((x + 24, 430), sub, font=font(22), fill=FG_MUTED)
        x += box_w + 50
    a1 = ((W - 3 * box_w - 100) // 2) + box_w + 6
    a2 = a1 + box_w + 50
    d.text((a1, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((a2, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((96, 600), "Three tools: get_pr_summary, list_pr_files, get_pr_diff.", font=font(30), fill=FG)
    d.text((96, 650), "Canned fixtures (stub mode) or the real GitHub REST API.", font=font(30), fill=FG)
    d.text((96, 770), "FunctionChoiceBehavior.Auto lets Gemini decide which tools to call.", font=font(28, italic=True), fill=FG_MUTED)


def draw_review(img, d):
    base(img, d, title="The review", eyebrow="Real Vertex AI run")
    d.text((96, 320), "PR: replace auth library with new in-house JWT", font=font(34), fill=FG)
    d.text((96, 365), "+1,842 / -947 across 23 files. src/auth/jwt.ts is new, 612 lines.",
           font=font(28, italic=True), fill=FG_MUTED)
    d.rounded_rectangle([(96, 430), (W - 96, H - 130)], radius=16, fill=PANEL)
    d.text((130, 460), "VERDICT: NEEDS_MORE_INFO", font=font(38, mono=True), fill=ACCENT_3)
    d.text((130, 510), "RISK:    HIGH",            font=font(38, mono=True), fill=ACCENT_3)
    d.text((130, 580), "EVIDENCE:", font=font(28, mono=True), fill=FG)
    bullets = [
        "Title indicates critical security changes.",
        "src/auth/jwt.ts added with 612 lines.",
        "1842 additions / 947 deletions across 23 files.",
    ]
    y = 620
    for b in bullets:
        d.text((150, y), "• " + b, font=font(26), fill=FG)
        y += 40
    d.text((130, 780), "NEXT STEP:", font=font(28, mono=True), fill=FG)
    d.text((150, 820), "Provide full diff for security review.", font=font(26), fill=FG)


def draw_code(img, d):
    base(img, d, title="The implementation", eyebrow="Six lines of Semantic Kernel")
    code = (
        "from semantic_kernel import Kernel\n"
        "from semantic_kernel.connectors.ai.google.vertex_ai import (\n"
        "    VertexAIChatCompletion,\n"
        ")\n"
        "\n"
        "kernel = Kernel()\n"
        "kernel.add_service(VertexAIChatCompletion(\n"
        "    project_id='careersavvy-mukunda',\n"
        "    gemini_model_id='gemini-2.5-flash',\n"
        "))\n"
        "kernel.add_plugin(GitHubPRPlugin(stub=True),\n"
        "                  plugin_name='github')"
    )
    d.rounded_rectangle([(96, 320), (W - 96, H - 130)], radius=18, fill=CODE_BG)
    yy = 360
    for line in code.split("\n"):
        d.text((130, yy), line, font=font(26, mono=True), fill=CODE_FG)
        yy += 42


def draw_close(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.text((96, 200), "agent-academy-msft", font=font(86), fill=FG)
    d.rectangle([(96, 310), (340, 320)], fill=ACCENT)
    d.text((96, 360), "github.com/MukundaKatta/agent-academy-msft", font=font(36, mono=True), fill=ACCENT)
    d.text((96, 440), "agent-academy-msft-1029931682737.us-central1.run.app", font=font(34, mono=True), fill=ACCENT_2)
    d.text((96, 560), "Microsoft Semantic Kernel", font=font(34), fill=FG_MUTED)
    d.text((96, 610), "+ Vertex AI Gemini 2.5 Flash", font=font(34), fill=FG_MUTED)
    d.text((96, 660), "+ canned GitHub PR fixtures (real-API ready)", font=font(34), fill=FG_MUTED)
    d.text((96, 820), "Apache 2.0. Mukunda Katta, independent.", font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 865), "Submission for Agent Academy (Microsoft) hackathon.", font=font(28, italic=True), fill=FG_MUTED)


SLIDES = [
    Slide("01_title",
          "Agent academy M S F T. A pull request reviewer agent on Microsoft Semantic Kernel plus Gemini.",
          draw_title),
    Slide("02_problem",
          "Every Friday afternoon, someone opens an eighteen hundred line pull request that touches auth and asks for a fast review. The reviewer needs to figure out, is this risky, is there enough test coverage, does it touch security boundaries, can I approve. The agent does the first pass in seven seconds.",
          draw_problem),
    Slide("03_microsoft",
          "The Microsoft product is Semantic Kernel, Microsoft's open source agent S D K. Kernel, kernel function, function choice behavior. It's provider agnostic. This build routes through Vertex A I Gemini two point five flash via S K's Vertex A I Chat Completion connector. Swap Azure Chat Completion in five lines if you have Azure. That's the point. The agent shape is portable across L L Ms.",
          draw_microsoft),
    Slide("04_architecture",
          "Three boxes. A repo and P R number go into a Semantic Kernel agent powered by Gemini. The agent calls three kernel function tools, get P R summary, list P R files, get P R diff. Canned fixtures for demos. Real Git Hub R E S T A P I one env var away. Function choice behavior auto lets Gemini decide which tools to call.",
          draw_architecture),
    Slide("05_review",
          "Here's a real review from a Vertex A I run. The pull request replaces the auth library with a new in house J W T. Eighteen hundred forty two additions, nine forty seven deletions, twenty three files. The agent verdicts needs more info, risk high. It cites the six twelve line new auth file, the total diff size, and asks the author to provide the full diff for security review.",
          draw_review),
    Slide("06_code",
          "The whole agent fits in twelve lines. One Kernel, one Vertex A I Chat Completion service, one plugin. Function choice behavior auto handles tool routing. The kernel function plugin exposes get P R summary, list P R files, get P R diff to the model.",
          draw_code),
    Slide("07_close",
          "Agent academy M S F T. Apache two point zero. Submission for the Agent Academy hackathon, Microsoft track. Thank you.",
          draw_close),
]


def render_slides(outdir):
    paths = []
    for sl in SLIDES:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        sl.draw(img, d)
        p = outdir / f"{sl.name}.png"
        img.save(p, "PNG", optimize=True)
        paths.append(p)
        print(f"  rendered {p.name}")
    return paths


def render_audio(outdir):
    paths = []
    for sl in SLIDES:
        wav = outdir / f"{sl.name}.aiff"
        m4a = outdir / f"{sl.name}.m4a"
        subprocess.run(["say", "-v", "Samantha", "-r", "175", "-o", str(wav), sl.narration], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                        "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
        wav.unlink(missing_ok=True)
        paths.append(m4a)
        print(f"  spoke   {m4a.name}")
    return paths


def render_segments(outdir, slide_pngs, audio_m4as):
    segs = []
    for sl, png, m4a in zip(SLIDES, slide_pngs, audio_m4as):
        out = outdir / f"seg_{sl.name}.mp4"
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(m4a)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        seg_dur = float(dur) + 0.4
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-i", str(m4a),
            "-af", "apad=pad_dur=0.4",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-r", "30", "-t", f"{seg_dur:.2f}",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", str(out),
        ], check=True)
        segs.append(out)
        print(f"  segment {out.name}  ({seg_dur:.2f}s)")
    return segs


def concat(outdir, segs):
    list_file = outdir / "concat.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in segs) + "\n")
    out = outdir / "demo.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ], check=True)
    return out


def main():
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "agent-academy-msft" / ".video-build"
    outdir.mkdir(parents=True, exist_ok=True)
    for needed in ("ffmpeg", "ffprobe", "say"):
        if shutil.which(needed) is None:
            sys.exit(f"missing tool: {needed}")
    print("[1/4] slides...")
    slides = render_slides(outdir)
    print("[2/4] audio...")
    audios = render_audio(outdir)
    print("[3/4] segments...")
    segs = render_segments(outdir, slides, audios)
    print("[4/4] concat...")
    final = concat(outdir, segs)
    size = final.stat().st_size / (1024 * 1024)
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
        capture_output=True, text=True,
    ).stdout.strip()
    print(f"\nDONE: {final}  ({size:.1f} MB, {float(dur):.1f}s)")


if __name__ == "__main__":
    main()
