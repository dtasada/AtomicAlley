from .engine import *
from math import floor


class TextWriter:
    def __init__(
        self, content, pos, font_size, color, anchor="topleft", writer_speed=0.25
    ):
        self.index = 0.0
        self.show = True
        self.writer_speed = writer_speed
        self.font_size = font_size
        self.body_pos = pos
        self.body_texs = [
            fonts[font_size].render(
                content[:i] + "_" if i < len(content) else content[:i], False, color
            )
            for i in range(len(content) + 1)
        ]
        self.body_rects = [
            self.body_texs[i].get_rect() for i in range(len(self.body_texs))
        ]
        [setattr(br, anchor, pos) for br in self.body_rects]

    def start(self):
        self.show = True

    def kill(self):
        self.index = 0
        self.show = False

    def update(self):
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            if self.index < len(self.body_texs) - 1:
                self.index = len(self.body_texs) - 1
            else:
                self.kill()

        display.blit(
            self.body_texs[floor(self.index)], self.body_rects[floor(self.index)]
        )
        target = self.index + self.writer_speed
        if target < len(self.body_texs):
            self.index = target


class Dialogue(TextWriter):
    def __init__(self, content, speaker):
        self.margin = 16
        self.back_color = Colors.GRAYS[32]
        self.body_color = Colors.WHITE
        self.speaker = speaker  # speaker is the character that says the thing
        size = (display.get_width() - self.margin * 2, 320)
        self.master_rect = pygame.Rect(
            (self.margin, display.get_height() - size[1] - self.margin),
            size,
        )
        self.speaker_tex = fonts[FontSize.SUBTITLE].render(
            self.speaker, ANTI_ALIASING, self.body_color
        )
        self.speaker_rect = self.speaker_tex.get_rect(
            topleft=(
                self.margin * 2,
                display.get_height() - self.master_rect.height - self.margin / 2,
            )
        )
        super().__init__(  # careful not to overwrite anything here
            content,
            self.master_rect.topleft,
            FontSize.BODY,
            Colors.WHITE,
        )
        for rect in self.body_rects:
            rect.topleft = (
                rect.left + self.margin,
                self.speaker_rect.bottom + self.margin / 2,
            )

    def update(self):
        if self.show:
            pygame.draw.rect(
                display, self.back_color, self.master_rect, border_radius=BORDER_RADIUS
            )  # render box
            display.blit(self.speaker_tex, self.speaker_rect)  # render speaker
            super().update()  # render body
