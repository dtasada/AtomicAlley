from .engine import *
from .buttons import *
from .writers import *
from .artifacts import *
from .player import *

from typing import List

import sys


class Interactive:
    "Interactive item that is found in-game, like a workbench, or floor loot"
    DIALOGUE = 0
    MUT_STATE = 1
    MUT_PLAYER = 2

    def __init__(
        self,
        description,
        tex_path,
        world_pos: v2,
        do,
        player_effect: Effect | None = None,
        dialogues: List[Dialogue] | None = None,
        target_state: States | None = None,
        other_lambda: LambdaType | None = None,
    ):
        self.focused = False
        self.description = description
        self.anchor = "midleft" if "tiles" in tex_path.as_posix() else "center"
        self.tex = pygame.transform.scale_by(
            pygame.image.load(tex_path).convert_alpha(), R
        )
        self.rect = self.tex.get_rect()
        self.do = do
        self.other_lambda = other_lambda
        self.wpos = world_pos  # world pos, not blit pos
        self.prompt = TextWriter(
            f"{self.description}: press <e> to interact",
            (display.width / 2, display.height * 2 / 3),
            FontSize.SMALL,
            Colors.WHITE,
            anchor="center",
            writer_speed=1.25,
        )

        self.dialogues = dialogues
        self.target_state = target_state
        if self.do == Interactive.DIALOGUE and not self.dialogues:
            print(
                "Error: Interactive object has type of DIALOGUE but no given dialogues"
            )
            sys.exit(1)
        elif self.do == Interactive.MUT_STATE and not target_state:
            print(
                "Error: Interactive object has type of MUT_STATE but no given `state_target`"
            )
            sys.exit(1)
        elif self.do == Interactive.MUT_PLAYER and not player_effect:
            print(
                "Error: Interactive object has type of MUT_PLAYER but no given `player_effect`"
            )
            sys.exit(1)

    def update(self, player, interactives):
        setattr(self.rect, self.anchor, v2_sub(cart_to_iso(*self.wpos, 0), game.scroll))

        # update interactives
        self.focused = (
            sorted(
                interactives,  # only focus the closest to player
                key=lambda i_: v2_len(v2_sub(i_.wpos, player.wpos)),
                reverse=False,
            )[0]
            == self
        ) and v2_len(v2_sub(self.wpos, player.wpos)) <= 3

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

                if self.other_lambda:
                    self.other_lambda()
        else:
            self.prompt.kill()

        display.blit(self.tex, self.rect)
