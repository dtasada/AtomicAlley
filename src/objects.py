from .engine import *
from .buttons import *
from .writers import *
from .atoms import *

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
        image,
        world_pos: v2,
        do: "Interactive | None" = None,
        player_effect: List[Atom] | None = None,
        dialogues: List[Dialogue] | None = None,
        target_state: States | None = None,
        other_lambda: LambdaType | None = None,
        anchor: str | None = None,
    ):
        self.focused = False
        self.description = description
        self.anchor = anchor or "topleft"
        self.image = image
        self.rect = self.image.get_rect()
        self.do = do
        self.other_lambda = other_lambda
        self.wpos = world_pos  # world pos, not blit pos
        self.prompt = TextWriter(
            f"{self.description}: press <e> to interact",
            (display.get_width() / 2, display.get_height() * 2 / 3),
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
    
    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                match self.do:
                    case Interactive.DIALOGUE:
                        game.dialogue = self.dialogues[0]
                        game.dialogue.start()
                    case Interactive.MUT_STATE:
                        game.set_state(self.target_state)

                if self.other_lambda:
                    self.other_lambda(self)
            
    def update(self):
        setattr(self.rect, self.anchor, v2_sub(cart_to_iso(*self.wpos, 1), game.scroll))

        display.blit(self.image, self.rect)

        if self.focused:  # self.focused gets updated in main loop | yes it does indeed
            self.prompt.start()
            self.prompt.update()
        else:
            self.prompt.kill()
        