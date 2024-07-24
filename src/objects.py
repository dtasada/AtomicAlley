from .engine import *
from .buttons import *
from .writers import *

import sys


class Interactive:
    DIALOGUE = 0
    MUT_STATE = 1
    MUT_PLAYER = 2

    def __init__(
        self, description, tex_path, pos: v2, do, dialogues=None, target_state=None
    ):
        self.focused = False
        self.description = description
        self.target_state = target_state
        self.tex = pygame.transform.scale_by(
            pygame.image.load(tex_path).convert_alpha(), R
        )
        self.rect = self.tex.get_rect()
        self.do = do
        self.pos = pos  # world pos, not blit pos
        self.prompt = TextWriter(
            f"{self.description}: press <e> to interact",
            (display.width / 2, display.height * 2 / 3),
            FontSize.BODY,
            Colors.WHITE,
            anchor="center",
            writer_speed=1.25,
        )
        self.dialogues = dialogues
        if self.do == Interactive.DIALOGUE and not self.dialogues:
            print(
                "Error: Interactive object has type of DIALOGUE but no given dialogues"
            )
            sys.exit(1)
        elif self.do == Interactive.MUT_STATE and not target_state:
            print(
                "Error: Interactive object has type of MUT_STATE but no given state_target"
            )
            sys.exit(1)

    def update(self, player, interactives):
        self.rect.midleft = v2_sub(cart_to_iso(*self.pos, 0), game.scroll)
        display.blit(self.tex, self.rect)

        # update interactives

        self.focused = (
            sorted(
                interactives,  # only focus the closest to player
                key=lambda i_: v2_len(v2_sub(i_.pos, player.pos)),
                reverse=False,
            )[0]
            == self
        ) and v2_len(v2_sub(self.pos, player.pos)) <= 3

        if self.focused:  # self.focused gets updated in main loop
            self.prompt.start()
            self.prompt.update()

            if pygame.key.get_just_pressed()[pygame.K_e]:
                match self.do:
                    case Interactive.DIALOGUE:
                        game.dialogue = self.dialogues[0]
                        game.dialogue.start()
                    case Interactive.MUT_STATE:
                        game.set_state(self.target_state)
        else:
            self.prompt.kill()
