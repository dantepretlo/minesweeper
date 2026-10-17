import os
import sys
import time
import random
import ctypes
import math
import pygame

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

    WM_NCLBUTTONDOWN = 0x00A1
    WM_SETICON = 0x0080
    HTCAPTION = 2

    ICON_SMALL = 0
    ICON_BIG = 1

    SW_MINIMIZE = 6

    GWL_STYLE = -16
    GWL_EXSTYLE = -20

    WS_CAPTION = 0x00C00000
    WS_THICKFRAME = 0x00040000
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    WS_SYSMENU = 0x00080000

    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010
    SWP_FRAMECHANGED = 0x0020

    LR_LOADFROMFILE = 0x0010
    IMAGE_ICON = 1

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]


# ============================================================
# COLORS
# ============================================================

GRAY = (192, 192, 192)
LIGHT_GRAY = (223, 223, 223)
MID_GRAY = (160, 160, 160)
DARK_GRAY = (128, 128, 128)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
DARK_RED = (65, 0, 0)
YELLOW = (255, 255, 0)

XP_BORDER = (49, 106, 197)
MENU_BLUE = (0, 0, 128)

NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

DIFFICULTIES = {
    "Beginner": (9, 9, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (30, 16, 99),
}

TILE = 24

TITLE_HEIGHT = 30
MENU_HEIGHT = 22
HEADER_HEIGHT = 76

SIDE_MARGIN = 12
BOTTOM_MARGIN = 12

FPS = 60

FONT_MENU = pygame.font.SysFont("Tahoma", 11)
FONT_TITLE = pygame.font.SysFont("Tahoma", 13, bold=True)
FONT_NUMBERS = pygame.font.SysFont("Arial", 18, bold=True)

clock = pygame.time.Clock()


# ============================================================
# GRAPHICS HELPERS
# ============================================================

def gradient(surface, rect, top, bottom):
    x, y, w, h = rect

    if w <= 0 or h <= 0:
        return

    for i in range(h):
        t = i / max(1, h - 1)

        color = tuple(
            int(top[k] + (bottom[k] - top[k]) * t)
            for k in range(3)
        )

        pygame.draw.line(
            surface,
            color,
            (x, y + i),
            (x + w - 1, y + i),
        )


def bevel(surface, rect, raised=True):
    x, y, w, h = rect

    if w <= 1 or h <= 1:
        return

    if raised:
        top = WHITE
        bottom = DARK_GRAY
        inner_top = LIGHT_GRAY
        inner_bottom = MID_GRAY
    else:
        top = DARK_GRAY
        bottom = WHITE
        inner_top = MID_GRAY
        inner_bottom = LIGHT_GRAY

    pygame.draw.line(
        surface, top,
        (x, y), (x + w - 1, y),
    )

    pygame.draw.line(
        surface, top,
        (x, y), (x, y + h - 1),
    )

    pygame.draw.line(
        surface, bottom,
        (x, y + h - 1), (x + w - 1, y + h - 1),
    )

    pygame.draw.line(
        surface, bottom,
        (x + w - 1, y), (x + w - 1, y + h - 1),
    )

    if w > 4 and h > 4:
        pygame.draw.line(
            surface, inner_top,
            (x + 1, y + 1), (x + w - 2, y + 1),
        )

        pygame.draw.line(
            surface, inner_top,
            (x + 1, y + 1), (x + 1, y + h - 2),
        )

        pygame.draw.line(
            surface, inner_bottom,
            (x + 1, y + h - 2),
            (x + w - 2, y + h - 2),
        )

        pygame.draw.line(
            surface, inner_bottom,
            (x + w - 2, y + 1),
            (x + w - 2, y + h - 2),
        )


def raised_panel(surface, rect):
    pygame.draw.rect(surface, GRAY, rect)
    bevel(surface, rect, True)


def sunken_panel(surface, rect):
    pygame.draw.rect(surface, GRAY, rect)
    bevel(surface, rect, False)


# ============================================================
# WINDOWS API HELPERS
# ============================================================

def get_hwnd():
    if not IS_WINDOWS:
        return None

    try:
        return pygame.display.get_wm_info().get("window")
    except Exception:
        return None


def configure_window():
    if not IS_WINDOWS:
        return

    hwnd = get_hwnd()

    if not hwnd:
        return

    try:
        user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
        user32.GetWindowLongPtrW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
        ]

        user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
        user32.SetWindowLongPtrW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_ssize_t,
        ]

        user32.SetWindowPos.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]

        style = user32.GetWindowLongPtrW(hwnd, GWL_STYLE)

        style &= ~WS_CAPTION
        style &= ~WS_THICKFRAME
        style &= ~WS_MAXIMIZEBOX

        style |= WS_SYSMENU | WS_MINIMIZEBOX

        user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)

        exstyle = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)

        exstyle &= ~WS_EX_TOOLWINDOW
        exstyle |= WS_EX_APPWINDOW

        user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, exstyle)

        user32.SetWindowPos(
            hwnd,
            None,
            0, 0, 0, 0,
            SWP_NOMOVE
            | SWP_NOSIZE
            | SWP_NOZORDER
            | SWP_NOACTIVATE
            | SWP_FRAMECHANGED,
        )

    except Exception as exc:
        print("Window configuration warning:", exc)


def apply_rounded_corners():
    if not IS_WINDOWS:
        return

    hwnd = get_hwnd()

    if not hwnd:
        return

    region = None

    try:
        user32.GetWindowRect.restype = ctypes.c_int
        user32.GetWindowRect.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(RECT),
        ]

        rect = RECT()

        if not user32.GetWindowRect(
            hwnd, ctypes.byref(rect)
        ):
            return

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if width <= 0 or height <= 0:
            return

        gdi32.CreateRoundRectRgn.restype = ctypes.c_void_p
        gdi32.CreateRoundRectRgn.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        user32.SetWindowRgn.restype = ctypes.c_int
        user32.SetWindowRgn.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
        ]

        gdi32.DeleteObject.argtypes = [ctypes.c_void_p]

        region = gdi32.CreateRoundRectRgn(
            0, 0, width, height, 12, 12
        )

        if region:
            result = user32.SetWindowRgn(
                hwnd, region, True
            )

            if result:
                region = None

    except Exception as exc:
        print("Rounded-corner warning:", exc)

    finally:
        if region:
            try:
                gdi32.DeleteObject(region)
            except Exception:
                pass


def refresh_window_shape():
    if not IS_WINDOWS:
        return

    pygame.event.pump()
    configure_window()
    pygame.event.pump()
    apply_rounded_corners()


def set_windows_icon():
    if not IS_WINDOWS:
        return

    hwnd = get_hwnd()

    if not hwnd:
        return

    if getattr(sys, "frozen", False):
        folder = os.path.dirname(sys.executable)
    else:
        folder = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(folder, "minesweeper.ico")

    if not os.path.isfile(icon_path):
        return

    try:
        user32.LoadImageW.restype = ctypes.c_void_p
        user32.LoadImageW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]

        small = user32.LoadImageW(
            None, icon_path, IMAGE_ICON, 16, 16,
            LR_LOADFROMFILE,
        )

        large = user32.LoadImageW(
            None, icon_path, IMAGE_ICON, 32, 32,
            LR_LOADFROMFILE,
        )

        user32.SendMessageW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]

        if small:
            user32.SendMessageW(
                hwnd, WM_SETICON, ICON_SMALL, small
            )

        if large:
            user32.SendMessageW(
                hwnd, WM_SETICON, ICON_BIG, large
            )

    except Exception as exc:
        print("Icon warning:", exc)


def minimize_window():
    hwnd = get_hwnd()

    if IS_WINDOWS and hwnd:
        user32.ShowWindow(hwnd, SW_MINIMIZE)


def drag_window():
    hwnd = get_hwnd()

    if IS_WINDOWS and hwnd:
        user32.ReleaseCapture()
        user32.SendMessageW(
            hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0
        )


# ============================================================
# SEVEN-SEGMENT COUNTERS
# ============================================================

SEGMENTS = {
    "0": "abcdef",
    "1": "bc",
    "2": "abged",
    "3": "abgcd",
    "4": "fgbc",
    "5": "afgcd",
    "6": "afgecd",
    "7": "abc",
    "8": "abcdefg",
    "9": "abfgcd",
    "-": "g",
}


def draw_digit(surface, x, y, char):
    active = SEGMENTS.get(char, "")

    parts = {
        "a": ((x + 4, y + 1), (x + 10, y + 1)),
        "g": ((x + 4, y + 12), (x + 10, y + 12)),
        "d": ((x + 4, y + 23), (x + 10, y + 23)),
        "f": ((x + 2, y + 3), (x + 2, y + 10)),
        "b": ((x + 12, y + 3), (x + 12, y + 10)),
        "e": ((x + 2, y + 14), (x + 2, y + 21)),
        "c": ((x + 12, y + 14), (x + 12, y + 21)),
    }

    for name, (start, end) in parts.items():
        color = RED if name in active else DARK_RED

        pygame.draw.line(
            surface, color, start, end, 3
        )


def draw_counter(surface, x, y, value):
    w, h = 52, 34

    pygame.draw.rect(
        surface, BLACK, (x, y, w, h)
    )

    pygame.draw.line(
        surface, DARK_GRAY,
        (x, y), (x + w - 1, y), 2,
    )

    pygame.draw.line(
        surface, DARK_GRAY,
        (x, y), (x, y + h - 1), 2,
    )

    pygame.draw.line(
        surface, WHITE,
        (x, y + h - 1), (x + w - 1, y + h - 1), 2,
    )

    pygame.draw.line(
        surface, WHITE,
        (x + w - 1, y), (x + w - 1, y + h - 1), 2,
    )

    value = max(-99, min(999, int(value)))
    text = f"{value:03d}"

    for i, char in enumerate(text):
        draw_digit(
            surface, x + 4 + i * 16, y + 4, char
        )


# ============================================================
# MINES AND FLAGS
# ============================================================

def draw_mine(surface, x, y):
    cx = x + TILE // 2
    cy = y + TILE // 2

    pygame.draw.line(
        surface, BLACK,
        (cx - 10, cy), (cx + 10, cy), 2,
    )

    pygame.draw.line(
        surface, BLACK,
        (cx, cy - 10), (cx, cy + 10), 2,
    )

    pygame.draw.line(
        surface, BLACK,
        (cx - 7, cy - 7), (cx + 7, cy + 7), 2,
    )

    pygame.draw.line(
        surface, BLACK,
        (cx - 7, cy + 7), (cx + 7, cy - 7), 2,
    )

    pygame.draw.circle(
        surface, BLACK, (cx, cy), 7
    )

    pygame.draw.circle(
        surface, WHITE, (cx - 2, cy - 2), 2
    )


def draw_flag(surface, x, y):
    pygame.draw.line(
        surface, BLACK,
        (x + 8, y + 4), (x + 8, y + 20), 2,
    )

    pygame.draw.polygon(
        surface, RED,
        [
            (x + 9, y + 4),
            (x + 19, y + 8),
            (x + 9, y + 13),
        ],
    )

    pygame.draw.line(
        surface, BLACK,
        (x + 4, y + 20), (x + 14, y + 20), 2,
    )


# ============================================================
# WINDOWS XP MINESWEEPER SMILEY FACE
# ============================================================

def draw_face(surface, cx, cy, expression):
    """
    Draw the classic Minesweeper face.

    happy      = normal smile
    surprised  = pressed mouse button
    dead       = mine hit, X eyes
    win        = sunglasses
    """

    # Classic raised square button.
    size = 34

    rect = pygame.Rect(
        cx - size // 2,
        cy - size // 2,
        size,
        size,
    )

    raised_panel(surface, rect)

    # Slightly smaller circular outline and yellow face.
    # The black outline is drawn first.
    pygame.draw.circle(
        surface, BLACK, (cx, cy), 12
    )

    pygame.draw.circle(
        surface, YELLOW, (cx, cy), 10
    )

    # Tiny highlight on the upper-left side.
    pygame.draw.arc(
        surface,
        (255, 255, 170),
        (cx - 8, cy - 8, 14, 14),
        math.radians(135),
        math.radians(225),
        1,
    )

    # --------------------------------------------------------
    # DEAD FACE: X-shaped eyes and a frown
    # --------------------------------------------------------

    if expression == "dead":
        for ex in (cx - 4, cx + 4):
            pygame.draw.line(
                surface,
                BLACK,
                (ex - 2, cy - 5),
                (ex + 2, cy - 1),
                2,
            )

            pygame.draw.line(
                surface,
                BLACK,
                (ex + 2, cy - 5),
                (ex - 2, cy - 1),
                2,
            )

        # Frown.
        pygame.draw.arc(
            surface,
            BLACK,
            (cx - 6, cy + 1, 12, 8),
            math.radians(35),
            math.radians(145),
            2,
        )

    # --------------------------------------------------------
    # WIN FACE: BLACK SUNGLASSES AND A SMILE
    # --------------------------------------------------------

    elif expression == "win":
        # Left sunglass lens.
        pygame.draw.rect(
            surface,
            BLACK,
            (cx - 9, cy - 5, 7, 5),
        )

        # Right sunglass lens.
        pygame.draw.rect(
            surface,
            BLACK,
            (cx + 2, cy - 5, 7, 5),
        )

        # Bridge between the lenses.
        pygame.draw.line(
            surface,
            BLACK,
            (cx - 2, cy - 3),
            (cx + 2, cy - 3),
            2,
        )

        # Smile.
        pygame.draw.arc(
            surface,
            BLACK,
            (cx - 6, cy - 2, 12, 9),
            math.radians(200),
            math.radians(340),
            2,
        )

    # --------------------------------------------------------
    # SURPRISED FACE: OPEN EYES AND O-SHAPED MOUTH
    # --------------------------------------------------------

    elif expression == "surprised":
        # Eyes.
        pygame.draw.circle(
            surface,
            BLACK,
            (cx - 4, cy - 3),
            2,
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (cx + 4, cy - 3),
            2,
        )

        # Open mouth.
        pygame.draw.ellipse(
            surface,
            BLACK,
            (cx - 2, cy + 2, 4, 6),
        )

        pygame.draw.ellipse(
            surface,
            WHITE,
            (cx - 1, cy + 3, 2, 3),
        )

    # --------------------------------------------------------
    # NORMAL FACE: DOT EYES AND CURVED SMILE
    # --------------------------------------------------------

    else:
        pygame.draw.circle(
            surface,
            BLACK,
            (cx - 4, cy - 3),
            1,
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (cx + 4, cy - 3),
            1,
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (cx - 6, cy - 3, 12, 9),
            math.radians(200),
            math.radians(340),
            2,
        )


# ============================================================
# MINESWEEPER GAME
# ============================================================

class Minesweeper:

    def __init__(self, difficulty="Intermediate"):
        self.difficulty = difficulty

        self.cols, self.rows, self.mine_count = (
            DIFFICULTIES[difficulty]
        )

        self.menu_open = False
        self.help_open = False
        self.menu_items = []
        self.help_items = []

        self.hover_button = None
        self.dialog = None
        self.dialog_button = None

        # Tracks whether the mouse is currently held over a
        # covered board square.
        self.mouse_down_cell = None

        pygame.display.set_caption("Minesweeper")

        self.calculate_dimensions()
        self.reset()

        configure_window()

        pygame.event.pump()
        pygame.time.delay(200)

        self.select_difficulty(self.difficulty)

        pygame.event.pump()
        pygame.time.delay(100)

        refresh_window_shape()
        set_windows_icon()

        pygame.time.delay(100)
        apply_rounded_corners()

    # ========================================================
    # DIMENSIONS
    # ========================================================

    def calculate_dimensions(self):
        self.width = SIDE_MARGIN * 2 + self.cols * TILE

        self.board_top = (
            TITLE_HEIGHT + MENU_HEIGHT + HEADER_HEIGHT + 12
        )

        self.height = (
            self.board_top
            + self.rows * TILE
            + BOTTOM_MARGIN
        )

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

    # ========================================================
    # DIFFICULTY SELECTION
    # ========================================================

    def select_difficulty(self, difficulty):
        if difficulty not in DIFFICULTIES:
            return

        self.difficulty = difficulty

        self.cols, self.rows, self.mine_count = (
            DIFFICULTIES[difficulty]
        )

        self.calculate_dimensions()
        self.reset()

        pygame.event.pump()

        if IS_WINDOWS:
            pygame.time.delay(80)
            refresh_window_shape()
            set_windows_icon()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        self.board = [
            [0 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.revealed = [
            [False for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.flags = [
            [False for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.started = False
        self.game_over = False
        self.won = False

        self.start_time = None
        self.elapsed = 0

        self.exploded = None

        # Always start a new game with the normal smiley.
        self.face = "happy"

        self.mouse_down_cell = None

        self.menu_open = False
        self.help_open = False

        self.dialog = None
        self.dialog_button = None

    # ========================================================
    # GAME LOGIC
    # ========================================================

    def neighbors(self, x, y):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue

                nx = x + dx
                ny = y + dy

                if (
                    0 <= nx < self.cols
                    and 0 <= ny < self.rows
                ):
                    yield nx, ny

    def place_mines(self, safe_x, safe_y):
        available = [
            (x, y)
            for y in range(self.rows)
            for x in range(self.cols)
            if (x, y) != (safe_x, safe_y)
        ]

        for x, y in random.sample(
            available,
            self.mine_count,
        ):
            self.board[y][x] = -1

        for y in range(self.rows):
            for x in range(self.cols):
                if self.board[y][x] == -1:
                    continue

                self.board[y][x] = sum(
                    self.board[ny][nx] == -1
                    for nx, ny in self.neighbors(x, y)
                )

    def reveal(self, x, y):
        if self.game_over:
            return

        if self.flags[y][x] or self.revealed[y][x]:
            return

        if not self.started:
            self.place_mines(x, y)
            self.started = True
            self.start_time = time.monotonic()

        self.revealed[y][x] = True

        if self.board[y][x] == -1:
            self.game_over = True
            self.face = "dead"
            self.exploded = (x, y)

            self.elapsed = int(
                time.monotonic() - self.start_time
            )

            return

        if self.board[y][x] == 0:
            for nx, ny in self.neighbors(x, y):
                if (
                    not self.revealed[ny][nx]
                    and not self.flags[ny][nx]
                ):
                    self.reveal(nx, ny)

        self.check_win()

    def toggle_flag(self, x, y):
        if self.game_over or self.revealed[y][x]:
            return

        self.flags[y][x] = not self.flags[y][x]

        self.check_win()

    def chord(self, x, y):
        if self.game_over or not self.revealed[y][x]:
            return

        number = self.board[y][x]

        if number <= 0:
            return

        adjacent = list(self.neighbors(x, y))

        flag_count = sum(
            self.flags[ny][nx]
            for nx, ny in adjacent
        )

        if flag_count != number:
            return

        for nx, ny in adjacent:
            if self.game_over:
                break

            if (
                not self.flags[ny][nx]
                and not self.revealed[ny][nx]
            ):
                self.reveal(nx, ny)

    def check_win(self):
        if self.game_over:
            return

        safe_cells = (
            self.cols * self.rows - self.mine_count
        )

        revealed_count = sum(
            self.revealed[y][x]
            for y in range(self.rows)
            for x in range(self.cols)
        )

        if revealed_count == safe_cells:
            self.game_over = True
            self.won = True
            self.face = "win"

            if self.started:
                self.elapsed = int(
                    time.monotonic() - self.start_time
                )

            for y in range(self.rows):
                for x in range(self.cols):
                    if self.board[y][x] == -1:
                        self.flags[y][x] = True

    # ========================================================
    # TITLE BAR BUTTONS
    # ========================================================

    def draw_title_mine(self, x, y):
        cx = x + 10
        cy = y + 10

        pygame.draw.line(
            self.screen, BLACK,
            (cx - 8, cy), (cx + 8, cy), 2,
        )

        pygame.draw.line(
            self.screen, BLACK,
            (cx, cy - 8), (cx, cy + 8), 2,
        )

        pygame.draw.line(
            self.screen, BLACK,
            (cx - 6, cy - 6), (cx + 6, cy + 6), 2,
        )

        pygame.draw.line(
            self.screen, BLACK,
            (cx - 6, cy + 6), (cx + 6, cy - 6), 2,
        )

        pygame.draw.circle(
            self.screen, BLACK, (cx, cy), 6
        )

        pygame.draw.circle(
            self.screen, WHITE, (cx - 2, cy - 2), 2
        )

    def title_button_rect(self, kind):
        positions = {
            "minimize": (self.width - 72, 5, 20, 19),
            "maximize": (self.width - 49, 5, 20, 19),
            "close": (self.width - 26, 5, 21, 19),
        }

        return pygame.Rect(*positions[kind])

    def draw_title_button(self, kind):
        rect = self.title_button_rect(kind)

        x, y, w, h = rect
        hovered = self.hover_button == kind

        if kind == "close":
            if hovered:
                top = (255, 190, 145)
                bottom = (235, 55, 25)
                edge = (255, 225, 180)
            else:
                top = (255, 155, 130)
                bottom = (190, 20, 15)
                edge = (255, 190, 160)

            gradient(self.screen, rect, top, bottom)

            pygame.draw.rect(
                self.screen, edge, rect, 1
            )

            pygame.draw.line(
                self.screen, (125, 0, 0),
                (x + 2, y + h - 2),
                (x + w - 3, y + h - 2),
            )

            pygame.draw.line(
                self.screen, (100, 0, 0),
                (x + 5, y + 4),
                (x + w - 5, y + h - 4), 4,
            )

            pygame.draw.line(
                self.screen, (100, 0, 0),
                (x + w - 5, y + 4),
                (x + 5, y + h - 4), 4,
            )

            pygame.draw.line(
                self.screen, WHITE,
                (x + 5, y + 4),
                (x + w - 5, y + h - 4), 2,
            )

            pygame.draw.line(
                self.screen, WHITE,
                (x + w - 5, y + 4),
                (x + 5, y + h - 4), 2,
            )

        elif kind == "maximize":
            if hovered:
                top = (200, 220, 240)
                bottom = (115, 155, 200)
            else:
                top = (167, 193, 220)
                bottom = (105, 140, 180)

            gradient(self.screen, rect, top, bottom)

            pygame.draw.rect(
                self.screen, (145, 165, 190), rect, 1
            )

            pygame.draw.rect(
                self.screen, (95, 105, 120),
                (x + 5, y + 4, 10, 10), 2,
            )

            pygame.draw.line(
                self.screen, (190, 200, 211),
                (x + 7, y + 6), (x + 13, y + 6),
            )

        else:
            if hovered:
                top = (180, 225, 255)
                bottom = (20, 105, 220)
                edge = (225, 245, 255)
            else:
                top = (135, 205, 255)
                bottom = (0, 65, 180)
                edge = (180, 225, 255)

            gradient(self.screen, rect, top, bottom)

            pygame.draw.rect(
                self.screen, edge, rect, 1
            )

            pygame.draw.line(
                self.screen, (225, 245, 255),
                (x + 2, y + 1),
                (x + w - 3, y + 1),
            )

            pygame.draw.line(
                self.screen, (0, 35, 105),
                (x + 5, y + 14),
                (x + 15, y + 14), 3,
            )

            pygame.draw.line(
                self.screen, WHITE,
                (x + 5, y + 12),
                (x + 15, y + 12), 2,
            )

    def draw_title_bar(self):
        gradient(
            self.screen,
            (0, 0, self.width, TITLE_HEIGHT),
            (9, 151, 255),
            (0, 52, 150),
        )

        pygame.draw.line(
            self.screen, (120, 205, 255),
            (4, 1), (self.width - 5, 1),
        )

        pygame.draw.line(
            self.screen, (0, 40, 125),
            (2, TITLE_HEIGHT - 2),
            (self.width - 3, TITLE_HEIGHT - 2),
        )

        self.draw_title_mine(5, 5)

        title = FONT_TITLE.render(
            "Minesweeper", True, WHITE
        )

        self.screen.blit(title, (28, 7))

        self.draw_title_button("minimize")
        self.draw_title_button("maximize")
        self.draw_title_button("close")

    # ========================================================
    # MENU BAR
    # ========================================================

    def draw_menu_bar(self):
        y = TITLE_HEIGHT

        pygame.draw.rect(
            self.screen, GRAY,
            (0, y, self.width, MENU_HEIGHT),
        )

        game_rect = pygame.Rect(
            5, y + 1, 48, MENU_HEIGHT - 2
        )

        help_rect = pygame.Rect(
            57, y + 1, 48, MENU_HEIGHT - 2
        )

        if self.menu_open:
            pygame.draw.rect(
                self.screen, MENU_BLUE, game_rect
            )

        if self.help_open:
            pygame.draw.rect(
                self.screen, MENU_BLUE, help_rect
            )

        game_color = WHITE if self.menu_open else BLACK
        help_color = WHITE if self.help_open else BLACK

        self.screen.blit(
            FONT_MENU.render("Game", True, game_color),
            (10, y + 5),
        )

        self.screen.blit(
            FONT_MENU.render("Help", True, help_color),
            (62, y + 5),
        )

    # ========================================================
    # GAME MENU
    # ========================================================

    def draw_game_menu(self):
        mx = 5
        my = TITLE_HEIGHT + MENU_HEIGHT
        mw = 155

        items = [
            ("New", "F2"),
            ("separator", ""),
            ("Beginner", ""),
            ("Intermediate", ""),
            ("Expert", ""),
            ("separator", ""),
            ("Exit", ""),
        ]

        mh = 8 + sum(
            7 if label == "separator" else 23
            for label, _ in items
        )

        raised_panel(
            self.screen, (mx, my, mw, mh)
        )

        self.menu_items = []

        y = my + 4

        for label, shortcut in items:
            if label == "separator":
                pygame.draw.line(
                    self.screen, DARK_GRAY,
                    (mx + 5, y + 2),
                    (mx + mw - 5, y + 2),
                )

                pygame.draw.line(
                    self.screen, WHITE,
                    (mx + 5, y + 3),
                    (mx + mw - 5, y + 3),
                )

                y += 7
                continue

            item_rect = pygame.Rect(
                mx + 2, y, mw - 4, 23
            )

            self.menu_items.append((item_rect, label))

            self.screen.blit(
                FONT_MENU.render(label, True, BLACK),
                (mx + 10, y + 5),
            )

            if shortcut:
                image = FONT_MENU.render(
                    shortcut, True, BLACK
                )

                self.screen.blit(
                    image,
                    (
                        mx + mw - image.get_width() - 10,
                        y + 5,
                    ),
                )

            y += 23

    # ========================================================
    # HELP MENU
    # ========================================================

    def draw_help_menu(self):
        mx = 57
        my = TITLE_HEIGHT + MENU_HEIGHT
        mw = 190

        items = [
            ("How to play", "help"),
            ("About Minesweeper", "about"),
        ]

        mh = 8 + len(items) * 23

        raised_panel(
            self.screen, (mx, my, mw, mh)
        )

        self.help_items = []

        for i, (label, action) in enumerate(items):
            y = my + 4 + i * 23

            rect = pygame.Rect(
                mx + 2, y, mw - 4, 23
            )

            self.help_items.append((rect, action))

            self.screen.blit(
                FONT_MENU.render(label, True, BLACK),
                (mx + 10, y + 5),
            )

    def draw_help_dialog(self, title, lines):
        w = min(300, self.width - 24)
        line_height = 20
        h = 70 + len(lines) * line_height

        x = (self.width - w) // 2
        y = (self.height - h) // 2

        shadow = pygame.Surface(
            (w + 8, h + 8), pygame.SRCALPHA
        )

        shadow.fill((0, 0, 0, 75))

        self.screen.blit(
            shadow, (x + 4, y + 4)
        )

        raised_panel(self.screen, (x, y, w, h))

        gradient(
            self.screen,
            (x + 3, y + 3, w - 6, 23),
            (9, 151, 255),
            (0, 52, 150),
        )

        self.screen.blit(
            FONT_TITLE.render(title, True, WHITE),
            (x + 9, y + 7),
        )

        for i, line in enumerate(lines):
            self.screen.blit(
                FONT_MENU.render(line, True, BLACK),
                (x + 12, y + 36 + i * line_height),
            )

        button = pygame.Rect(
            x + w - 72, y + h - 29, 60, 21
        )

        raised_panel(self.screen, button)

        label = FONT_MENU.render("OK", True, BLACK)

        self.screen.blit(
            label, label.get_rect(center=button.center)
        )

        self.dialog_button = button

    # ========================================================
    # HEADER
    # ========================================================

    def draw_header(self):
        y = TITLE_HEIGHT + MENU_HEIGHT

        raised_panel(
            self.screen,
            (
                6, y + 4,
                self.width - 12,
                HEADER_HEIGHT - 4,
            ),
        )

        flag_count = sum(
            sum(row) for row in self.flags
        )

        draw_counter(
            self.screen,
            18,
            y + 25,
            self.mine_count - flag_count,
        )

        if self.started:
            if self.game_over:
                elapsed = self.elapsed
            else:
                elapsed = int(
                    time.monotonic() - self.start_time
                )
        else:
            elapsed = 0

        draw_counter(
            self.screen,
            self.width - 70,
            y + 25,
            min(999, elapsed),
        )

        # Draw the current face expression.
        draw_face(
            self.screen,
            self.width // 2,
            y + 38,
            self.face,
        )

    # ========================================================
    # BOARD
    # ========================================================

    def draw_board(self):
        bx = SIDE_MARGIN
        by = self.board_top

        sunken_panel(
            self.screen,
            (
                bx - 4,
                by - 4,
                self.cols * TILE + 8,
                self.rows * TILE + 8,
            ),
        )

        for y in range(self.rows):
            for x in range(self.cols):
                px = bx + x * TILE
                py = by + y * TILE

                rect = (px, py, TILE, TILE)

                revealed = self.revealed[y][x]
                flagged = self.flags[y][x]
                value = self.board[y][x]

                if self.exploded == (x, y):
                    pygame.draw.rect(
                        self.screen, RED, rect
                    )

                    draw_mine(self.screen, px, py)
                    continue

                if self.game_over and not self.won:
                    if value == -1:
                        pygame.draw.rect(
                            self.screen, GRAY, rect
                        )

                        pygame.draw.rect(
                            self.screen, DARK_GRAY, rect, 1
                        )

                        draw_mine(self.screen, px, py)
                        continue

                    if flagged:
                        raised_panel(self.screen, rect)
                        draw_flag(self.screen, px, py)

                        pygame.draw.line(
                            self.screen, RED,
                            (px + 3, py + 3),
                            (px + TILE - 3, py + TILE - 3),
                            2,
                        )

                        pygame.draw.line(
                            self.screen, RED,
                            (px + TILE - 3, py + 3),
                            (px + 3, py + TILE - 3),
                            2,
                        )

                        continue

                if revealed:
                    pygame.draw.rect(
                        self.screen, GRAY, rect
                    )

                    pygame.draw.rect(
                        self.screen, MID_GRAY, rect, 1
                    )

                    if value > 0:
                        image = FONT_NUMBERS.render(
                            str(value),
                            True,
                            NUMBER_COLORS[value],
                        )

                        self.screen.blit(
                            image,
                            image.get_rect(
                                center=(
                                    px + TILE // 2,
                                    py + TILE // 2,
                                )
                            ),
                        )

                    elif value == -1:
                        draw_mine(self.screen, px, py)

                else:
                    raised_panel(self.screen, rect)

                    if flagged:
                        draw_flag(self.screen, px, py)

    # ========================================================
    # MAIN DRAW
    # ========================================================

    def draw(self):
        self.screen.fill(GRAY)

        self.draw_title_bar()
        self.draw_menu_bar()
        self.draw_header()
        self.draw_board()

        if self.menu_open:
            self.draw_game_menu()

        elif self.help_open:
            self.draw_help_menu()

        border_rect = pygame.Rect(
            1, 1,
            self.width - 2,
            self.height - 2,
        )

        pygame.draw.rect(
            self.screen,
            XP_BORDER,
            border_rect,
            width=2,
        )

        if self.dialog is not None:
            title, lines = self.dialog
            self.draw_help_dialog(title, lines)

        pygame.display.flip()

    # ========================================================
    # MENU ACTIONS
    # ========================================================

    def handle_menu_click(self, mx, my):
        for rect, label in self.menu_items:
            if rect.collidepoint(mx, my):
                if label == "New":
                    self.reset()

                elif label in DIFFICULTIES:
                    self.select_difficulty(label)

                elif label == "Exit":
                    pygame.quit()
                    sys.exit()

                return True

        return False

    def handle_help_click(self, mx, my):
        for rect, action in self.help_items:
            if rect.collidepoint(mx, my):
                if action == "help":
                    self.dialog = (
                        "How to play",
                        [
                            "Left-click a square to reveal it.",
                            "Right-click to place or remove a flag.",
                            "Numbers show nearby mines.",
                            "Avoid mines to win!",
                            "Press F2 to start a new game.",
                        ],
                    )

                elif action == "about":
                    self.dialog = (
                        "About Minesweeper",
                        [
                            "Classic-style Minesweeper.",
                            "Inspired by Windows XP.",
                            "Created with Python and Pygame.",
                        ],
                    )

                self.help_open = False
                return True

        return False

    # ========================================================
    # TITLE BAR INPUT
    # ========================================================

    def handle_title_click(self, mx, my):
        if my >= TITLE_HEIGHT:
            return False

        if self.title_button_rect("close").collidepoint(mx, my):
            pygame.quit()
            sys.exit()

        if self.title_button_rect("minimize").collidepoint(mx, my):
            minimize_window()
            return True

        if self.title_button_rect("maximize").collidepoint(mx, my):
            return True

        drag_window()
        return True

    def update_hover(self):
        mx, my = pygame.mouse.get_pos()

        self.hover_button = None

        if my < TITLE_HEIGHT:
            for kind in (
                "minimize",
                "maximize",
                "close",
            ):
                if self.title_button_rect(
                    kind
                ).collidepoint(mx, my):
                    self.hover_button = kind
                    break

    # ========================================================
    # MOUSE POSITION HELPERS
    # ========================================================

    def board_cell_at(self, mx, my):
        gx = (mx - SIDE_MARGIN) // TILE
        gy = (my - self.board_top) // TILE

        if (
            0 <= gx < self.cols
            and 0 <= gy < self.rows
        ):
            return gx, gy

        return None

    def face_at(self, mx, my):
        face_x = self.width // 2
        face_y = TITLE_HEIGHT + MENU_HEIGHT + 38

        return (
            abs(mx - face_x) <= 17
            and abs(my - face_y) <= 17
        )

    # ========================================================
    # EVENT LOOP
    # ========================================================

    def run(self):
        running = True

        while running:
            clock.tick(FPS)

            self.update_hover()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                # ------------------------------------------------
                # KEYBOARD
                # ------------------------------------------------

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.dialog is not None:
                            self.dialog = None

                        elif self.menu_open or self.help_open:
                            self.menu_open = False
                            self.help_open = False

                        else:
                            running = False

                    elif event.key == pygame.K_F2:
                        self.reset()

                # ------------------------------------------------
                # MOUSE BUTTON PRESSED
                # ------------------------------------------------

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if event.button == 1:

                        # Dialog.
                        if self.dialog is not None:
                            if (
                                self.dialog_button
                                and self.dialog_button.collidepoint(
                                    mx, my
                                )
                            ):
                                self.dialog = None

                            continue

                        # Custom title bar.
                        if my < TITLE_HEIGHT:
                            self.handle_title_click(mx, my)
                            continue

                        # Menu bar.
                        if (
                            TITLE_HEIGHT <= my
                            < TITLE_HEIGHT + MENU_HEIGHT
                        ):
                            if 5 <= mx < 55:
                                self.help_open = False
                                self.menu_open = not self.menu_open
                                continue

                            if 57 <= mx < 107:
                                self.menu_open = False
                                self.help_open = not self.help_open
                                continue

                            self.menu_open = False
                            self.help_open = False
                            continue

                        # Dropdown menus.
                        if self.menu_open:
                            if self.handle_menu_click(mx, my):
                                continue

                            self.menu_open = False

                        elif self.help_open:
                            if self.handle_help_click(mx, my):
                                continue

                            self.help_open = False

                        # Clicking the face resets the game.
                        if self.face_at(mx, my):
                            self.reset()
                            continue

                        # Only show the surprised expression while
                        # pressing an unrevealed, unflagged square.
                        cell = self.board_cell_at(mx, my)

                        if cell is not None:
                            gx, gy = cell

                            if (
                                not self.game_over
                                and not self.revealed[gy][gx]
                                and not self.flags[gy][gx]
                            ):
                                self.mouse_down_cell = cell
                                self.face = "surprised"

                    # Right-click places a flag.
                    elif event.button == 3:
                        if self.dialog is not None:
                            continue

                        cell = self.board_cell_at(mx, my)

                        if cell is not None:
                            gx, gy = cell
                            self.toggle_flag(gx, gy)

                # ------------------------------------------------
                # MOUSE BUTTON RELEASED
                # ------------------------------------------------

                elif event.type == pygame.MOUSEBUTTONUP:
                    mx, my = event.pos

                    if event.button == 1:

                        pressed_cell = self.mouse_down_cell

                        self.mouse_down_cell = None

                        # Do not change the dead or win face.
                        if self.game_over:
                            continue

                        # If the player was pressing a board square,
                        # reveal it only if the release is over that
                        # same square.
                        if pressed_cell is not None:
                            released_cell = self.board_cell_at(
                                mx, my
                            )

                            self.face = "happy"

                            if released_cell == pressed_cell:
                                gx, gy = pressed_cell

                                if self.revealed[gy][gx]:
                                    self.chord(gx, gy)
                                else:
                                    self.reveal(gx, gy)

                            # reveal() changes the face to dead if
                            # the selected square contains a mine.
                            # check_win() changes it to sunglasses
                            # if the player wins.
                            continue

            # Keep the surprised expression only while the left
            # mouse button is held over the original covered cell.
            if (
                not self.game_over
                and self.mouse_down_cell is not None
            ):
                buttons = pygame.mouse.get_pressed()

                if not buttons[0]:
                    self.mouse_down_cell = None
                    self.face = "happy"

            self.draw()

        pygame.quit()


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":
    game = Minesweeper("Intermediate")
    game.run()
