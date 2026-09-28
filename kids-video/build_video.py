#!/usr/bin/env python3
"""Build an original kids' phonics lesson: Bibi on her houseboat.

Teaches the sounds s, a, t, p, i, n, plus blending and segmenting.
The pictures are storybook illustrations; every letter is drawn here
so the spelling on screen stays accurate.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BUILD = ROOT / "build"
SLIDES = BUILD / "slides"
AUDIO = BUILD / "audio"
CLIPS = BUILD / "clips"
FONT_PATH = ASSETS / "Nunito.ttf"

W, H = 1920, 1080
VOICE = "en-GB-SoniaNeural"
RATE = "+0%"
PITCH = "-2Hz"
FPS = 30

INK = (61, 48, 38)
CREAM = (255, 250, 242)
CARD = (255, 253, 248)
LEAF = (47, 107, 78)

LETTER_COLORS = {
    "s": (224, 122, 95),
    "a": (214, 158, 46),
    "t": (38, 140, 128),
    "p": (190, 86, 116),
    "i": (70, 112, 168),
    "n": (62, 122, 90),
}

TRIOS = {
    "s": ("objects-s.png", ["sun", "sock", "snake"]),
    "a": ("objects-a.png", ["apple", "ant", "alligator"]),
    "t": ("objects-t.png", ["tiger", "tap", "top"]),
    "p": ("objects-p.png", ["pig", "pen", "pan"]),
    "i": ("objects-i.png", ["insect", "ink", "igloo"]),
    "n": ("objects-n.png", ["nest", "nose", "net"]),
}

# Spoken with ordinary words. The voice says these example words clearly,
# and the pictures show the letter that matches the first sound.
S = "sss"
A = "apple"
T = "tap"
P = "pig"
I = "insect"
N = "nest"
ESS = "S"
AY = "A"
TEE = "T"
PEE = "P"
EYE = "I"
EN = "N"
BIBI = "Bibi"


def lesson() -> list[dict]:
    """Original narration. Same early phonics goals as a SATPIN lesson,
    told by a new person in a new place."""
    return [
        dict(
            id="welcome",
            chapter="Welcome aboard",
            kind="scene",
            image="scene-welcome.png",
            kicker="Bibi's Houseboat Garden",
            caption="Hello, little gardeners.",
            say=(
                f"Hello, little gardeners. I am {BIBI}. "
                "Come and sit with me on my houseboat. The canal is quiet, "
                "the ducks are dozing, and the lanterns are ready for learning. "
                "Today we are going to learn phonics. Phonics means the sounds "
                "that letters make. When we know those sounds, we can begin to "
                "read words. If something feels tricky, that is okay. We will "
                "try it together. Every try helps your reading grow. Are you ready? "
                "Then let us begin."
            ),
        ),
        dict(
            id="listen",
            chapter="Warm up your ears",
            kind="scene",
            image="scene-listen.png",
            kicker="Listening ears",
            caption="Point to your ears.",
            say=(
                "First, let us warm up our listening ears. Point to your ears. "
                "There they are. I will say a word. You listen for the very first sound. "
                "The sun. sss. Tiger, like tap. Apple, like ant. Pig, like pen. "
                "You listened so carefully. Give yourself a tiny clap."
            ),
        ),
        dict(
            id="six",
            kind="tiles",
            letters="satpin",
            word="",
            title="Six sounds for today",
            say=(
                "We are going to meet six sounds. sss, like sun. "
                "The start of apple. The start of tap. The start of pig. "
                "The start of insect. And the start of nest. "
                "By the end of our time on the boat, we will use them to read words."
            ),
        ),
        dict(
            id="letter-s",
            chapter="The sound s",
            kind="teach",
            letter="s",
            sound="sss",
            hint="like a little snake",
            say=(
                "This is the letter S. The sound it makes is sss, like a little "
                "snake in the grass. Can you say sss? Lovely. A clean little sound, "
                "with nothing extra after it. Look at the sun, a sock, and a snake. They all begin with sss."
            ),
        ),
        dict(
            id="which-s",
            kind="choice",
            question="Which picture begins with s?",
            items=["apple", "pig", "sun"],
            answer=2,
            revealed=False,
            say=(
                f"Which picture begins with {S}? Is it the apple, the pig, or the sun? "
                "Have a little think."
            ),
        ),
        dict(
            id="which-s-yes",
            kind="choice",
            question="Sun begins with s",
            items=["apple", "pig", "sun"],
            answer=2,
            revealed=True,
            say=(
                "It is the sun. Sun begins with sss. Apple begins like ant. "
                "Pig begins like pen. If you needed a hint, you are still learning, "
                "and that is a good thing."
            ),
        ),
        dict(
            id="letter-a",
            chapter="The sound a",
            kind="teach",
            letter="a",
            sound="a",
            hint="as in apple",
            say=(
                "This is the letter A. Today we use the short sound at the start of apple. "
                "Listen. Apple. A little ant. Alligator. Alligator is a long word, "
                "and it still starts like apple."
            ),
        ),
        dict(
            id="letter-t",
            chapter="The sound t",
            kind="teach",
            letter="t",
            sound="t",
            hint="a tiny tap",
            say=(
                "This is the letter T. Listen to the start of tap. "
                "Tiger. Tap. Top. Say them with me. Tiger. Tap. Top. "
                "They all start like tap. You are doing so well."
            ),
        ),
        dict(
            id="letter-p",
            chapter="The sound p",
            kind="teach",
            letter="p",
            sound="p",
            hint="a little pop",
            say=(
                "This is the letter P. Listen to the start of pig. "
                "Pig. Pen. Pan. They all start like pig. "
                "I am proud of your careful listening."
            ),
        ),
        dict(
            id="letter-i",
            chapter="The sound i",
            kind="teach",
            letter="i",
            sound="i",
            hint="as in insect",
            say=(
                "This is the letter I. Today we use the short sound at the start of insect. "
                "Listen. Insect. Ink. Igloo. They all start like insect."
            ),
        ),
        dict(
            id="letter-n",
            chapter="The sound n",
            kind="teach",
            letter="n",
            sound="n",
            hint="as in nest",
            say=(
                "Our last new sound is the letter N. Listen to the start of nest. "
                "Nest. Nose. Net. They all start like nest. You have met all six."
            ),
        ),
        dict(
            id="recap",
            kind="tiles",
            letters="satpin",
            word="",
            title="Say them with Bibi",
            say=(
                "Let us remember them together. sss, like sun. "
                "Apple. Tap. Pig. Insect. Nest. "
                "Six sounds. You stayed with me, and I am really proud of you."
            ),
        ),
        dict(
            id="blend-intro",
            chapter="Blending words",
            kind="scene",
            image="scene-celebrate.png",
            kicker="Blending",
            caption="Say the sounds, then push them together.",
            say=(
                "Now we can read words. This is called blending. "
                "Blending means we say each sound, then we push the sounds together."
            ),
        ),
        dict(
            id="blend-sat",
            kind="tiles",
            letters="sat",
            word="sat",
            title="Push the sounds together",
            say="Watch the letters. Starts like sun. Then apple. Then tap. They make sat now. We read a word.",
        ),
        dict(
            id="blend-pin",
            kind="tiles",
            letters="pin",
            word="pin",
            title="Push the sounds together",
            say="Starts like pig. Then insect. Then nest. They make pin now.",
        ),
        dict(
            id="blend-tap",
            kind="tiles",
            letters="tap",
            word="tap",
            title="Push the sounds together",
            say="Starts like tiger. Then apple. Then pig. They make tap now.",
        ),
        dict(
            id="blend-sip",
            kind="tiles",
            letters="sip",
            word="sip",
            title="Push the sounds together",
            say="Starts like sun. Then insect. Then pig. They make sip now.",
        ),
        dict(
            id="blend-nap",
            kind="tiles",
            letters="nap",
            word="nap",
            title="Push the sounds together",
            say="Starts like nest. Then apple. Then pig. They make nap now.",
        ),
        dict(
            id="blend-pan",
            kind="tiles",
            letters="pan",
            word="pan",
            title="You are reading",
            say="Starts like pig. Then apple. Then nest. They make pan now. You are reading. That is wonderful.",
        ),
        dict(
            id="turn-sat",
            chapter="Your turn",
            kind="tiles",
            letters="sat",
            word="sat",
            title="Your turn",
            say=(
                "Your turn. Starts like sun. Then apple. Then tap. Have a little think. "
                "They make sat now. If you said it with me, that counts."
            ),
        ),
        dict(
            id="turn-pin",
            kind="tiles",
            letters="pin",
            word="pin",
            title="Your turn",
            say="Try this one. Starts like pig. Then insect. Then nest. Have a little think. They make pin now. Beautiful.",
        ),
        dict(
            id="turn-tin",
            kind="tiles",
            letters="tin",
            word="tin",
            title="Your turn",
            say="One more. Starts like tiger. Then insect. Then nest. Have a little think. They make a tin can. You are blending.",
        ),
        dict(
            id="seg-intro",
            chapter="Segmenting",
            kind="scene",
            image="scene-listen.png",
            kicker="Segmenting",
            caption="Break a word into sounds.",
            say=(
                "Now we do the opposite of blending. This is called segmenting. "
                "We take a word and break it into sounds. Segmenting helps us spell."
            ),
        ),
        dict(
            id="seg-tap",
            kind="tiles",
            letters="tap",
            word="tap",
            title="Tap has three sounds",
            highlight="all",
            say="Listen to tap. It starts like tiger. Then apple. Then pig.",
        ),
        dict(
            id="seg-sit",
            kind="tiles",
            letters="sit",
            word="sit",
            title="Sit has three sounds",
            say="Listen to sit. It starts like sun. Then insect. Then tap.",
        ),
        dict(
            id="seg-pan",
            kind="tiles",
            letters="pan",
            word="pan",
            title="Pan has three sounds",
            say="Listen to pan. It starts like pig. Then apple. Then nest. You are doing something real readers do.",
        ),
        dict(
            id="first-sun",
            chapter="First and last sounds",
            kind="picture-sound",
            picture="sun",
            label="sun",
            focus="first",
            sound="s",
            say="Let us listen for the first sound. The sun. sss.",
        ),
        dict(
            id="first-pig",
            kind="picture-sound",
            picture="pig",
            label="pig",
            focus="first",
            sound="p",
            say="Pig. It starts like pen.",
        ),
        dict(
            id="first-nest",
            kind="picture-sound",
            picture="nest",
            label="nest",
            focus="first",
            sound="n",
            say="Nest. It starts like nose.",
        ),
        dict(
            id="last-sat",
            kind="tiles",
            letters="sat",
            word="sat",
            title="What is the last sound?",
            highlight="last",
            say="Listen to sat. It ends like tap.",
        ),
        dict(
            id="last-pin",
            kind="tiles",
            letters="pin",
            word="pin",
            title="What is the last sound?",
            highlight="last",
            say="Listen to pin. It ends like nest.",
        ),
        dict(
            id="last-nap",
            kind="tiles",
            letters="nap",
            word="nap",
            title="What is the last sound?",
            highlight="last",
            say=(
                "Listen to nap. It ends like pig. You can hear a sound at the beginning "
                "and a sound at the end. That is clever listening."
            ),
        ),
        dict(
            id="silly",
            chapter="A silly word",
            kind="tiles",
            letters="tas",
            word="tas",
            title="A silly word we can still read",
            say=(
                "Sat on the deck is a real word. Now look at a silly one. "
                "It starts like tap. Then apple. Then sss. "
                "It is not a word we usually say. And look, you can still sound it out, "
                "because you used the sounds. That is what good readers do."
            ),
        ),
        dict(
            id="wiggle-in",
            chapter="Garden wiggle",
            kind="action",
            title="Garden wiggle",
            subtitle="Stand up if you can",
            say="Let us give our brains a tiny rest. Stand up if you can.",
        ),
        dict(
            id="wiggle-s",
            kind="action",
            title="sss",
            subtitle="Slither like a snake",
            say=f"When you hear {S}, slither like a snake. {S}. Slither, slither.",
        ),
        dict(
            id="wiggle-a",
            kind="action",
            title="a",
            subtitle="Pretend to bite an apple",
            say="When you hear the start of apple, pretend to bite an apple. Apple. Yum.",
        ),
        dict(
            id="wiggle-t",
            kind="action",
            title="t",
            subtitle="Tap your toes",
            say="When you hear the start of tap, tap your toes. Tap, tap, tap.",
        ),
        dict(
            id="wiggle-p",
            kind="action",
            title="p",
            subtitle="Pop a bubble",
            say="When you hear the start of pig, pop a bubble. Pop, pop.",
        ),
        dict(
            id="wiggle-i",
            kind="action",
            title="i",
            subtitle="Point to a tiny insect",
            say="When you hear the start of insect, point to a tiny insect. Insect. There it is.",
        ),
        dict(
            id="wiggle-n",
            kind="action",
            title="n",
            subtitle="Touch your nose",
            say="When you hear the start of nest, touch your nose. Nest.",
        ),
        dict(
            id="wiggle-out",
            kind="action",
            title="Have a wiggle",
            subtitle="Then sit back down",
            say="Have a little wiggle, then sit back down when you are ready.",
        ),
        dict(
            id="read-intro",
            chapter="Read eight words",
            kind="scene",
            image="scene-celebrate.png",
            kicker="Read with Bibi",
            caption="Look. Say the sounds. Push them together.",
            say=(
                "Let us read our words one more time. Look at the letters. "
                "Say the sounds. Then push them together."
            ),
        ),
        *[
            dict(
                id=f"read-{word}",
                kind="tiles",
                letters=word,
                word=word,
                title="Read",
                say=say,
            )
            for word, say in [
                ("sat", "Starts like sun. Then apple. Then tap. They make sat now."),
                ("pin", "Starts like pig. Then insect. Then nest. They make pin now."),
                ("sit", "Starts like sun. Then insect. Then tap. They make sit now."),
                ("tap", "Starts like tiger. Then apple. Then pig. They make tap now."),
                ("nap", "Starts like nest. Then apple. Then pig. They make nap now."),
                ("sip", "Starts like sun. Then insect. Then pig. They make sip now."),
                ("pan", "Starts like pig. Then apple. Then nest. They make pan now."),
                ("tin", "Starts like tiger. Then insect. Then nest. They make a tin can. Eight words. A big clap for you."),
            ]
        ],
        dict(
            id="goodbye",
            chapter="See you next time",
            kind="scene",
            image="scene-goodbye.png",
            kicker="You did it",
            caption="Bye, little gardener.",
            say=(
                "Little gardener, look what you did today on the houseboat. "
                "You learned six sounds, with sun, apple, tap, pig, insect, and nest. "
                "You listened for the first sound and the last sound. "
                "You broke words apart. That is segmenting. "
                "You pushed sounds together. That is blending. "
                "And you read sat, pin, tap, sip, nap, pan, sit, and a tin can. "
                "Nobody learns it all in one go. Practice is how reading grows, "
                "and you practiced today. You are clever. You are patient with yourself. "
                f"I am so glad you came to sit among the flowers. Keep having a go. "
                f"I will be here next time, with the lanterns and the ducks. "
                f"Bye, little gardener. You were wonderful."
            ),
        ),
    ]


def font(size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(FONT_PATH), size)
    face.set_variation_by_axes([weight])
    return face


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    resized = im.resize((int(sw * scale), int(sh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def fit(im: Image.Image, w: int, h: int) -> Image.Image:
    copy = im.convert("RGBA")
    copy.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(copy, ((w - copy.width) // 2, (h - copy.height) // 2), copy)
    return canvas


def circle(im: Image.Image, size: int) -> Image.Image:
    face = cover(im, (size, size)).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((1, 1, size - 2, size - 2), fill=255)
    face.putalpha(mask)
    return face


def text_size(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0], box[3] - box[1], box


def draw_center(draw, xy, text, face, fill):
    w, h, box = text_size(draw, text, face)
    x = xy[0] - w / 2 - box[0]
    y = xy[1] - h / 2 - box[1]
    draw.text((x, y), text, font=face, fill=fill)
    return w, h


def wrap(draw, text, face, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=face) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def round_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def shadow_panel(base: Image.Image, box, radius=36) -> ImageDraw.ImageDraw:
    x0, y0, x1, y1 = box
    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle(
        (x0 + 8, y0 + 14, x1 + 8, y1 + 14), radius=radius, fill=(90, 60, 30, 48)
    )
    shade = shade.filter(ImageFilter.GaussianBlur(8))
    base.alpha_composite(shade)
    draw = ImageDraw.Draw(base)
    round_rect(draw, box, radius, CARD)
    return draw


def load_images():
    scenes = {
        name: Image.open(ASSETS / name).convert("RGB")
        for name in [
            "scene-welcome.png",
            "scene-listen.png",
            "scene-celebrate.png",
            "scene-goodbye.png",
            "scene-wiggle.png",
        ]
    }
    portrait = Image.open(ASSETS / "bibi-portrait.png").convert("RGB")
    objects = {}
    for _key, (filename, labels) in TRIOS.items():
        image = Image.open(ASSETS / filename).convert("RGB")
        third = image.width // 3
        for index, label in enumerate(labels):
            crop = image.crop((index * third, 0, (index + 1) * third, image.height))
            arr = np.asarray(crop)
            mask = np.any(arr < 228, axis=2)
            ys, xs = np.where(mask)
            if len(xs):
                pad = 10
                crop = crop.crop(
                    (
                        max(0, xs.min() - pad),
                        max(0, ys.min() - pad),
                        min(crop.width, xs.max() + pad + 1),
                        min(crop.height, ys.max() + pad + 1),
                    )
                )
            objects[label] = crop
    return scenes, portrait, objects


def new_canvas() -> Image.Image:
    return Image.new("RGBA", (W, H), (*CREAM, 255))


def garden_bed(scenes, name: str) -> Image.Image:
    photo = cover(scenes[name], (W, H)).filter(ImageFilter.GaussianBlur(10))
    wash = Image.new("RGB", (W, H), (255, 244, 228))
    photo = Image.blend(photo, wash, 0.42)
    return photo.convert("RGBA")


def draw_scene(scenes, seg) -> Image.Image:
    photo = cover(scenes[seg["image"]], (W, H)).convert("RGBA")
    arr = np.asarray(photo).astype(np.float32)
    band = 360
    for i in range(band):
        y = H - band + i
        alpha = (i / band) * 0.38
        arr[y, :, :3] = arr[y, :, :3] * (1 - alpha) + np.array([48, 32, 24]) * alpha
    for i in range(180):
        alpha = (1 - i / 180) * 0.28
        arr[i, :, :3] = arr[i, :, :3] * (1 - alpha) + np.array([48, 32, 24]) * alpha
    base = Image.fromarray(arr.astype(np.uint8), "RGBA")
    draw = ImageDraw.Draw(base)
    kicker_font = font(42, 800)
    kicker = seg["kicker"]
    kw, kh, kbox = text_size(draw, kicker, kicker_font)
    pad_x, pad_y = 28, 14
    pill = (48, 40, 48 + kw + pad_x * 2, 40 + kh + pad_y * 2)
    round_rect(draw, pill, 24, (255, 250, 242, 235))
    draw.text((48 + pad_x - kbox[0], 40 + pad_y - kbox[1]), kicker, font=kicker_font, fill=INK)

    cap_font = font(58, 800)
    lines = wrap(draw, seg["caption"], cap_font, 1500)
    line_h = 70
    block_h = line_h * len(lines)
    widths = [text_size(draw, line, cap_font)[0] for line in lines]
    block_w = max(widths)
    cx0 = (W - block_w) // 2 - 40
    cy0 = H - 70 - block_h - 28
    round_rect(draw, (cx0, cy0, cx0 + block_w + 80, cy0 + block_h + 36), 32, (255, 250, 242, 238))
    for i, line in enumerate(lines):
        lw, lh, box = text_size(draw, line, cap_font)
        draw.text(((W - lw) / 2 - box[0], cy0 + 18 + i * line_h - box[1]), line, font=cap_font, fill=INK)
    return base.convert("RGB")


def draw_header(base, draw, portrait, title):
    face = circle(portrait, 96)
    base.alpha_composite(face, (72, 48))
    draw.text((188, 58), "Bibi's Houseboat Garden", font=font(28, 700), fill=LEAF)
    draw.text((188, 96), title, font=font(40, 800), fill=INK)


def draw_teach(scenes, portrait, objects, seg) -> Image.Image:
    base = garden_bed(scenes, "scene-welcome.png")
    draw = shadow_panel(base, (40, 28, 1880, 1048), 40)
    letter = seg["letter"]
    color = LETTER_COLORS[letter]
    draw_header(base, draw, portrait, f"The letter {letter}")
    cx, cy, r = 390, 500, 148
    draw.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=color)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 252, 247, 255))
    draw_center(draw, (cx, cy - 6), letter, font(200, 800), color)
    sound_y = cy + r + 72
    draw_center(draw, (cx, sound_y), seg["sound"], font(60, 800), color)
    draw_center(draw, (cx, sound_y + 62), seg["hint"], font(30, 700), INK)

    labels = TRIOS[letter][1]
    card_w, card_h = 340, 520
    gap = 28
    total = card_w * 3 + gap * 2
    x = 740 + (1100 - total) // 2
    y = 230
    name_font = font(40, 800)
    for label in labels:
        round_rect(draw, (x, y, x + card_w, y + card_h), 28, (255, 255, 255, 255), color, 6)
        pic = fit(objects[label], card_w - 40, card_h - 120)
        base.alpha_composite(pic, (x + 20, y + 16))
        draw_center(draw, (x + card_w / 2, y + card_h - 52), label, name_font, INK)
        x += card_w + gap
    return base.convert("RGB")


def draw_choice(scenes, portrait, objects, seg) -> Image.Image:
    base = garden_bed(scenes, "scene-welcome.png")
    draw = shadow_panel(base, (40, 28, 1880, 1048), 40)
    draw_header(base, draw, portrait, seg["question"])
    card_w, card_h = 460, 620
    gap = 40
    total = card_w * 3 + gap * 2
    x = (W - total) // 2
    y = 250
    for index, name in enumerate(seg["items"]):
        chosen = seg["revealed"] and index == seg["answer"]
        outline = (214, 158, 46) if chosen else (230, 220, 206)
        width = 12 if chosen else 4
        round_rect(draw, (x, y, x + card_w, y + card_h), 32, (255, 255, 255, 255), outline, width)
        pic = fit(objects[name], card_w - 56, card_h - 170)
        base.alpha_composite(pic, (x + 28, y + 28))
        label_fill = (150, 104, 24) if chosen else INK
        draw_center(draw, (x + card_w / 2, y + card_h - 78), name, font(48, 800), label_fill)
        if chosen:
            draw_center(draw, (x + card_w / 2, y + card_h - 28), "this one", font(28, 800), (150, 104, 24))
        x += card_w + gap
    return base.convert("RGB")


def draw_tiles(scenes, portrait, seg) -> Image.Image:
    base = garden_bed(scenes, "scene-celebrate.png")
    draw = shadow_panel(base, (40, 28, 1880, 1048), 40)
    title = seg.get("title") or "Read the sounds"
    draw_header(base, draw, portrait, title)
    letters = list(seg["letters"])
    n = len(letters)
    tile = 280 if n <= 3 else 230 if n <= 4 else 200
    gap = 40 if n <= 4 else 26
    glyph_size = 148 if n <= 3 else 118 if n <= 4 else 96
    total = n * tile + (n - 1) * gap
    x = (W - total) // 2
    y = 330 if seg.get("word") else 390
    highlight = seg.get("highlight")
    for index, letter in enumerate(letters):
        color = LETTER_COLORS[letter]
        hot = highlight in (None, "all") or (
            highlight == "last" and index == n - 1
        ) or (highlight == "first" and index == 0)
        fill = (255, 252, 247, 255) if hot else (236, 230, 222, 255)
        outline = color if hot else (190, 180, 168)
        round_rect(draw, (x, y, x + tile, y + tile), 36, fill, outline, 8)
        draw_center(
            draw,
            (x + tile / 2, y + tile / 2 - 2),
            letter,
            font(glyph_size, 800),
            color if hot else (130, 120, 110),
        )
        x += tile + gap
    if seg.get("word"):
        draw_center(draw, (W / 2, y + tile + 110), seg["word"], font(84, 800), INK)
    return base.convert("RGB")


def draw_picture_sound(scenes, portrait, objects, seg) -> Image.Image:
    base = garden_bed(scenes, "scene-listen.png")
    draw = shadow_panel(base, (40, 28, 1880, 1048), 40)
    draw_header(base, draw, portrait, f"The first sound in {seg['label']}")
    color = LETTER_COLORS[seg["sound"]]
    round_rect(draw, (110, 230, 980, 990), 36, (255, 255, 255, 255))
    pic = fit(objects[seg["picture"]], 740, 520)
    base.alpha_composite(pic, (175, 270))
    draw_center(draw, (545, 900), seg["label"], font(64, 800), INK)
    draw.ellipse((1160, 300, 1720, 860), fill=color)
    draw.ellipse((1184, 324, 1696, 836), fill=(255, 252, 247, 255))
    draw_center(draw, (1440, 560), seg["sound"], font(240, 800), color)
    draw_center(draw, (1440, 940), "first sound", font(40, 800), INK)
    return base.convert("RGB")


def draw_action(scenes, seg) -> Image.Image:
    photo = cover(scenes["scene-wiggle.png"], (W, H)).convert("RGBA")
    veil = Image.new("RGBA", (W, H), (255, 246, 230, 70))
    photo.alpha_composite(veil)
    draw = ImageDraw.Draw(photo)
    round_rect(draw, (300, 200, 1620, 900), 48, (255, 250, 242, 232))
    title = seg["title"]
    short = len(title) <= 3
    size = 132 if short else 78
    color = LETTER_COLORS.get(title[:1], INK) if short else INK
    draw_center(draw, (960, 400), title, font(size, 800), color)
    draw_center(draw, (960, 700), seg["subtitle"], font(46, 800), INK)
    return photo.convert("RGB")


def render_slide(seg, scenes, portrait, objects) -> Image.Image:
    kind = seg["kind"]
    if kind == "scene":
        return draw_scene(scenes, seg)
    if kind == "teach":
        return draw_teach(scenes, portrait, objects, seg)
    if kind == "choice":
        return draw_choice(scenes, portrait, objects, seg)
    if kind == "tiles":
        return draw_tiles(scenes, portrait, seg)
    if kind == "picture-sound":
        return draw_picture_sound(scenes, portrait, objects, seg)
    if kind == "action":
        return draw_action(scenes, seg)
    raise ValueError(kind)


async def synth_all(segments: list[dict]) -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(3)

    async def one(seg):
        mp3 = AUDIO / f"{seg['id']}.mp3"
        wav = AUDIO / f"{seg['id']}.wav"
        if wav.exists() and wav.stat().st_size > 1000:
            return
        async with sem:
            last_error = None
            for attempt in range(4):
                try:
                    comm = edge_tts.Communicate(seg["say"], VOICE, rate=RATE, pitch=PITCH)
                    await comm.save(str(mp3))
                    last_error = None
                    break
                except Exception as exc:  # network blip
                    last_error = exc
                    await asyncio.sleep(1.5 * (attempt + 1))
            if last_error:
                raise last_error
        pad_wav(mp3, wav)
        print(f"voice {seg['id']} {probe(wav):.1f}s", flush=True)

    await asyncio.gather(*[one(seg) for seg in segments])


def pad_wav(mp3: Path, wav: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3),
            "-af",
            "adelay=320|320,apad=pad_dur=0.5",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(wav),
        ]
    )


def probe(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def encode_segments(segments: list[dict]) -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)
    for seg in segments:
        clip = CLIPS / f"{seg['id']}.mp4"
        wav = AUDIO / f"{seg['id']}.wav"
        slide = SLIDES / f"{seg['id']}.png"
        if clip.exists() and clip.stat().st_size > 1000:
            continue
        duration = probe(wav)
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-i",
                str(slide),
                "-i",
                str(wav),
                "-t",
                f"{duration:.3f}",
                "-vf",
                "scale=1920:1080,format=yuv420p",
                "-r",
                str(FPS),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-tune",
                "stillimage",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-shortest",
                str(clip),
            ]
        )
        print(f"clip {seg['id']}", flush=True)


def make_music(path: Path, seconds: float = 900) -> None:
    sr = 44100
    phrase = [
        (392.0, 0.34),
        (0, 0.28),
        (440.0, 0.28),
        (0, 0.36),
        (523.25, 0.40),
        (0, 0.22),
        (493.88, 0.32),
        (0, 0.46),
        (440.0, 0.26),
        (392.0, 0.34),
        (349.23, 0.40),
        (0, 0.70),
        (329.63, 0.30),
        (0, 0.24),
        (392.0, 0.46),
        (0, 0.85),
    ]
    chunks = []
    total = 0
    while total < seconds:
        for freq, dur in phrase:
            n = int(sr * dur)
            t = np.arange(n) / sr
            if freq == 0:
                chunks.append(np.zeros(n))
            else:
                env = np.exp(-3.4 * t)
                tone = np.sin(2 * np.pi * freq * t) * 0.72
                tone += np.sin(2 * np.pi * freq * 2 * t) * 0.18
                chunks.append(tone * env * 0.22)
            total += dur
    audio = np.concatenate(chunks)[: int(sr * seconds)]
    audio = np.tanh(audio * 1.2) * 0.9
    stereo = np.column_stack([audio, audio])
    pcm = (stereo * 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sr)
        handle.writeframes(pcm.tobytes())


def assemble(segments: list[dict], final: Path) -> float:
    listing = BUILD / "concat.txt"
    lines = [f"file '{(CLIPS / (seg['id'] + '.mp4')).as_posix()}'" for seg in segments]
    listing.write_text("\n".join(lines) + "\n")
    silent = BUILD / "lesson-voice.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)])
    duration = probe(silent)
    music = BUILD / "music.wav"
    if not music.exists():
        make_music(music, seconds=max(30, duration + 5))
    fade_out = max(0, duration - 2.5)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(music),
            "-filter_complex",
            (
                f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
                f"volume=0.055,afade=t=in:st=0:d=1.4,afade=t=out:st={fade_out:.3f}:d=2.2[m];"
                "[0:a][m]amix=inputs=2:duration=first:normalize=0:dropout_transition=0[a]"
            ),
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    return duration


def thumbnail(scenes) -> Path:
    photo = cover(scenes["scene-welcome.png"], (1280, 720)).convert("RGBA")
    arr = np.asarray(photo).astype(np.float32)
    arr[:220, :, :3] = arr[:220, :, :3] * 0.72 + np.array([40, 26, 18]) * 0.28
    arr[500:, :, :3] = arr[500:, :, :3] * 0.55 + np.array([40, 26, 18]) * 0.45
    image = Image.fromarray(arr.astype(np.uint8), "RGBA")
    draw = ImageDraw.Draw(image)
    draw.text((56, 36), "Bibi's Houseboat", font=font(72, 800), fill=(255, 250, 242))
    draw.text((56, 120), "A phonics garden for kids", font=font(36, 700), fill=(255, 236, 210))
    letters = list("satpin")
    x = 56
    for letter in letters:
        color = LETTER_COLORS[letter]
        round_rect(draw, (x, 545, x + 180, 685), 24, (255, 250, 242, 245))
        draw_center(draw, (x + 90, 615), letter, font(78, 800), color)
        x += 198
    path = BUILD / "thumbnail.jpg"
    image.convert("RGB").save(path, quality=92)
    return path


def write_youtube(segments: list[dict], duration: float) -> None:
    times = []
    cursor = 0.0
    for seg in segments:
        if seg.get("chapter"):
            times.append((cursor, seg["chapter"]))
        cursor += probe(AUDIO / f"{seg['id']}.wav")
    def stamp(seconds: float) -> str:
        seconds = int(seconds)
        return f"{seconds // 60}:{seconds % 60:02d}"

    chapters = "\n".join(f"{stamp(t)} {name}" for t, name in times)
    description = f"""Bibi's Houseboat Garden | Phonics s a t p i n

Come aboard Bibi's cozy houseboat and learn the first sounds of reading.
This is a gentle, original lesson for young children.

Bibi teaches:
• the sounds s, a, t, p, i, and n
• listening for the first sound and the last sound
• blending sounds to read words
• segmenting words into sounds
• real words and one silly word
• a garden wiggle break

Words to read: sat, pin, tap, sip, nap, pan, sit, tin.

Learning takes practice. Every try counts.

Chapters
{chapters}

A calm lesson for little learners, about {int(duration // 60)} minutes.
"""
    (BUILD / "YOUTUBE.txt").write_text(description)
    (ROOT / "YOUTUBE.txt").write_text(description)


def main() -> None:
    slides_only = "--slides" in sys.argv
    for folder in (BUILD, SLIDES, AUDIO, CLIPS):
        folder.mkdir(parents=True, exist_ok=True)
    segments = lesson()
    scenes, portrait, objects = load_images()
    print(f"rendering {len(segments)} slides", flush=True)
    for seg in segments:
        image = render_slide(seg, scenes, portrait, objects)
        image.save(SLIDES / f"{seg['id']}.png")
    thumbnail(scenes)
    if slides_only:
        print("slides ready", flush=True)
        return
    asyncio.run(synth_all(segments))
    encode_segments(segments)
    final = BUILD / "bibi-houseboat-phonics.mp4"
    duration = assemble(segments, final)
    write_youtube(segments, duration)
    print(f"done {final} {duration:.1f}s", flush=True)


if __name__ == "__main__":
    main()
