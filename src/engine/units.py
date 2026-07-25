class Units:
    """
    Gestion centralisée des unités du logiciel.

    Toutes les dimensions du logiciel sont exprimées en millimètres.
    Les pixels ne servent qu'à l'affichage.
    """

    # ---------------------------------------------------------
    # Constantes
    # ---------------------------------------------------------

    MM_PER_INCH = 25.4
    POINTS_PER_INCH = 72.0

    # Valeur provisoire.
    # Elle sera remplacée plus tard par le zoom du Viewport.
    PIXELS_PER_MM = 2.834645669

    # ---------------------------------------------------------
    # Millimètres
    # ---------------------------------------------------------

    @classmethod
    def mm_to_px(cls, mm: float) -> float:

        return mm * cls.PIXELS_PER_MM

    @classmethod
    def px_to_mm(cls, px: float) -> float:

        return px / cls.PIXELS_PER_MM

    # ---------------------------------------------------------
    # Centimètres
    # ---------------------------------------------------------

    @classmethod
    def cm_to_mm(cls, cm: float) -> float:

        return cm * 10.0

    @classmethod
    def mm_to_cm(cls, mm: float) -> float:

        return mm / 10.0

    # ---------------------------------------------------------
    # Pouces
    # ---------------------------------------------------------

    @classmethod
    def inch_to_mm(cls, inch: float) -> float:

        return inch * cls.MM_PER_INCH

    @classmethod
    def mm_to_inch(cls, mm: float) -> float:

        return mm / cls.MM_PER_INCH

    # ---------------------------------------------------------
    # Points typographiques
    # ---------------------------------------------------------

    @classmethod
    def pt_to_mm(cls, pt: float) -> float:

        return (pt / cls.POINTS_PER_INCH) * cls.MM_PER_INCH

    @classmethod
    def mm_to_pt(cls, mm: float) -> float:

        return (mm / cls.MM_PER_INCH) * cls.POINTS_PER_INCH