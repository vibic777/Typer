"""Generate Typer's PNG window icon and multi-size Windows ICO asset."""

from PIL import Image, ImageDraw


def make_icon() -> Image.Image:
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 248, 248), radius=54, fill="#142847")
    draw.rounded_rectangle(
        (25, 70, 231, 186), radius=17, fill="#203b60", outline="#41638c", width=5
    )

    for y, keys in ((96, (47, 88, 129, 170)), (137, (55, 96, 137))):
        for x in keys:
            draw.rounded_rectangle(
                (x, y, x + 31, y + 27), radius=6, fill="#f4f8fc"
            )
    draw.rounded_rectangle((137, 137, 201, 164), radius=6, fill="#f4f8fc")

    draw.line((194, 38, 194, 63), fill="#35d4d0", width=7)
    draw.line((185, 55, 194, 64, 203, 55), fill="#35d4d0", width=7)
    draw.ellipse((188, 180, 236, 228), fill="#16b8b2", outline="#091426", width=7)
    for x in (205, 212, 219):
        draw.line((x, 195, x, 213), fill="white", width=4)
    return image


def main() -> None:
    icon = make_icon()
    icon.save("icon.png", format="PNG", optimize=True)
    sizes = (16, 24, 32, 48, 64, 128, 256)
    icon.save(
        "icon.ico",
        format="ICO",
        sizes=[(size, size) for size in sizes],
    )


if __name__ == "__main__":
    main()
