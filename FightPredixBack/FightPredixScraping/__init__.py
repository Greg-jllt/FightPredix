from FightPredixBack.FightPredixScraping.lib_page_combattant_ufc import (
    _extraire_info_combattant,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_front_page_ufc import (
    _page_principal_UFC,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_ufc_stats import (
    _cherche_combattant_UFC_stats,
    _ratrappage_manquants,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_combats import (
    _main_combat_recolte,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_arbitre import _main_arbitre  # noqa F401

from FightPredixBack.FightPredixScraping.lib_scraping_tapology import (
    _main_scraping_tapology,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_nettoyage_tapology import (
    _main_nettoyage_tapology,
)  # noqa F401

from FightPredixBack.FightPredixScraping.lib_join_ufc_tapology import (
    _main_tapology,
)  # noqa F401

from FightPredixBack.outils import configure_logger  # noqa F401
