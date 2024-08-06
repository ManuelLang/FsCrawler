#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

from app.config.config import CURRENT_MAX_AGE
from app.models.content import ContentClassificationPegi

TAXOMONY_PATH_SEPARATOR = '/'


class Taxonomy:
    def __init__(self, name, parent=None, color=None, min_age: ContentClassificationPegi = None) -> None:
        super().__init__()
        self.name = name
        self.color = color
        self.min_age: ContentClassificationPegi = min_age
        self.parent = parent
        self._children = []
        if parent:
            parent._children.append(self)
        self._path: str = self.path
        self._depth: int = self.depth


    @property
    def path(self) -> str:
        if self.parent:
            return f"{self.parent.path}{TAXOMONY_PATH_SEPARATOR}{self.name}"
        else:
            return self.name

    @property
    def depth(self) -> int:
        if self.parent:
            return self.parent.depth + 1
        else:
            return 1

    @property
    def root(self):
        if self.parent:
            return self.parent.root
        else:
            return self

    def find_from_here(self, name: str):
        if str(name).lower().strip() in self.name.lower().strip():
            return self
        for child in self._children:
            res = child.find_from_here(name)
            if res:
                return res
        return None

    def should_render(self, current_selected_max_age: ContentClassificationPegi = None):
        if current_selected_max_age is None:
            current_selected_max_age = ContentClassificationPegi.classification_from_age(CURRENT_MAX_AGE)
        if self.min_age is None:
            return self.parent.should_render(current_selected_max_age) if self.parent else True
        if self.parent:
            self.parent.should_render(current_selected_max_age) and self.min_age.value <= current_selected_max_age.value
        return self.min_age.value <= current_selected_max_age.value

    def render(self, line_break: str='\r\n') -> str:
        res = str(self)
        for child in self._children:
            rendered_child = child.render()
            if rendered_child:
                res += line_break + rendered_child
        return res

    def __str__(self) -> str:
        if self.parent and not self.parent.should_render() or not self.should_render():
            return ''
        if self.parent:
            return f"{self.parent.depth * '  '}{self.name}"
        return self.name
        # return self.path


if __name__ == '__main__':
    root = Taxonomy('Dossiers', min_age=ContentClassificationPegi.classification_from_age(7))
    papiers = Taxonomy('Papiers', root)
    immobilier = Taxonomy('Immobilier', papiers)
    investissements = Taxonomy('Investissements', immobilier, min_age=ContentClassificationPegi.classification_from_age(18))
    compta = Taxonomy('Compta', investissements)
    rp = Taxonomy('RP', immobilier)
    factures = Taxonomy('Factures', papiers)
    edouard = Taxonomy('Edouard', root)
    ecole = Taxonomy('Ecole', edouard)
    manuel = Taxonomy('Manuel', root)
    travail = Taxonomy('Travail', manuel)
    roche = Taxonomy('Roche', travail)
    navify = Taxonomy('navify', roche)
    projets = Taxonomy('Projets', navify)
    cur = Taxonomy('CUR', projets)
    a_faire = Taxonomy('A faire', papiers)
    sorties = Taxonomy('Sorties', root)
    camping = Taxonomy('Camping', sorties)

    print(root.render())

    print("\nLooking for 'ro'...")
    root_dossiers = investissements.root
    branch_roche = root_dossiers.find_from_here('ro')
    print(branch_roche.path)

    films = Taxonomy('Films', min_age=ContentClassificationPegi.classification_from_age(3))
    action = Taxonomy('Action', films, min_age=ContentClassificationPegi.classification_from_age(13))
    comedie = Taxonomy('Comédie', films, min_age=ContentClassificationPegi.classification_from_age(7))
    anime = Taxonomy('Animé', films, min_age=ContentClassificationPegi.classification_from_age(3))
    manga = Taxonomy('Manga', anime, min_age=ContentClassificationPegi.classification_from_age(14))
    scifi = Taxonomy('Science-Fiction', films, min_age=ContentClassificationPegi.classification_from_age(12))
    drame = Taxonomy('Drame', films, min_age=ContentClassificationPegi.classification_from_age(13))
    adulte = Taxonomy('Adulte', films, min_age=ContentClassificationPegi.classification_from_age(18))

    print("\n" + films.render())




