from dataclasses import dataclass


@dataclass
class FigureDocument:
    figure_id: str
    caption: str
    source_image_path: str
    category: str = "Figure"


class FigureExtractor:
    def extract(self, _text: str) -> list[FigureDocument]:
        return []
