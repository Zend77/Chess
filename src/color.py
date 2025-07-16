class Color:
    """
    Simple class to hold a pair of colors for chess board theming.
    Used to define light and dark square colors for different visual themes.
    """
    
    def __init__(self, light, dark):
        self.light = light  # RGB color for light squares
        self.dark = dark    # RGB color for dark squares