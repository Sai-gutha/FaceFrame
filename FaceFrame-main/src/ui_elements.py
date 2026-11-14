import cv2

# Colours are BGR.
CARD_FILL = (248, 233, 214)    # light blue, #D6E9F8
CARD_BORDER = (216, 178, 122)  # a shade of the brand blue, for the outline
CARD_TITLE = (105, 66, 30)     # deep navy, #1E4269
CARD_BODY = (140, 104, 66)     # softer navy for the secondary line
CARD_HINT = (176, 150, 122)    # muted, for the dismiss hint


def _rounded_rect(frame, rect, radius, color, thickness=-1):
    """
    Draw a rounded rectangle. OpenCV has no primitive for this, so it is built
    from two overlapping rectangles plus four corner arcs.
    """
    x1, y1, x2, y2 = rect
    radius = max(0, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
    corners = ((x1 + radius, y1 + radius), (x2 - radius, y1 + radius),
               (x1 + radius, y2 - radius), (x2 - radius, y2 - radius))

    if thickness < 0:
        cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(frame, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        for c in corners:
            cv2.circle(frame, c, radius, color, -1, cv2.LINE_AA)
        return

    cv2.line(frame, (x1 + radius, y1), (x2 - radius, y1), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1 + radius, y2), (x2 - radius, y2), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1, y1 + radius), (x1, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x2, y1 + radius), (x2, y2 - radius), color, thickness, cv2.LINE_AA)
    for c, (start, end) in zip(corners, ((180, 270), (270, 360), (90, 180), (0, 90))):
        cv2.ellipse(frame, c, (radius, radius), 0, start, end, color, thickness, cv2.LINE_AA)


def _centered_text(frame, text, cx, y, scale, color, thickness):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    cv2.putText(frame, text, (cx - tw // 2, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thickness, cv2.LINE_AA)


def draw_glasses_prompt(frame):
    """
    Draw the dismissible "remove your glasses" card near the top of the frame.

    Shown unconditionally at the start of a scan rather than only when glasses
    are detected: a detector that is wrong tells someone to remove glasses they
    are not wearing, which is worse than asking everyone once.

    Returns the card's bounding box so the caller can hit-test clicks against
    it, matching draw_quit_button's contract.
    """
    h, w = frame.shape[:2]

    # Sized as a fraction of the frame so it holds up at other resolutions.
    card_w = max(360, min(int(w * 0.46), 620))
    card_h = max(96, int(card_w * 0.27))
    x1 = (w - card_w) // 2
    y1 = max(16, int(h * 0.035))
    x2, y2 = x1 + card_w, y1 + card_h
    radius = card_h // 4

    # Translucent fill so the face stays visible behind the card.
    overlay = frame.copy()
    _rounded_rect(overlay, (x1, y1, x2, y2), radius, CARD_FILL, -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
    _rounded_rect(frame, (x1, y1, x2, y2), radius, CARD_BORDER, 2)

    cx = x1 + card_w // 2
    title_scale = card_w / 720.0 + 0.34
    body_scale = card_w / 900.0 + 0.24

    _centered_text(frame, "Wearing glasses?", cx, y1 + int(card_h * 0.36),
                   title_scale, CARD_TITLE, 2)
    _centered_text(frame, "Please remove them for an accurate scan.", cx,
                   y1 + int(card_h * 0.62), body_scale, CARD_BODY, 1)
    _centered_text(frame, "Click this card or press D to dismiss", cx,
                   y1 + int(card_h * 0.86), body_scale * 0.82, CARD_HINT, 1)

    # Small close affordance in the top-right corner.
    cxx, cxy, arm = x2 - int(radius * 0.9), y1 + int(radius * 0.9), max(4, card_h // 18)
    cv2.line(frame, (cxx - arm, cxy - arm), (cxx + arm, cxy + arm), CARD_HINT, 2, cv2.LINE_AA)
    cv2.line(frame, (cxx - arm, cxy + arm), (cxx + arm, cxy - arm), CARD_HINT, 2, cv2.LINE_AA)

    return (x1, y1, x2, y2)


# Draw a red "Quit" button and return its bounding box
def draw_quit_button(frame):
    x1, y1, x2, y2 = 20, 20, 120, 60
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), -1)
    cv2.putText(frame, "Quit", (x1 + 25, y1 + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return (x1, y1, x2, y2)

# Check if (x, y) is inside a given button region
def is_inside_button(x, y, button_coords):
    x1, y1, x2, y2 = button_coords
    return x1 <= x <= x2 and y1 <= y <= y2

