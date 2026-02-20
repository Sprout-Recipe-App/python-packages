from enum import StrEnum, auto

from pydantic_core import core_schema


class CamelCaseEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_):
        parts = name.lower().split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])


class DietType(CamelCaseEnum):
    PESCATARIAN = auto()
    VEGETARIAN = auto()
    VEGAN = auto()
    RAW_VEGAN = auto()


class DishType(CamelCaseEnum):
    APPETIZER = auto()
    ENTREE = auto()
    SIDE_DISH = auto()
    DESSERT = auto()
    BEVERAGE = auto()
    SNACK = auto()
    CONDIMENT = auto()


class Cuisine(StrEnum):
    _ignore_ = ["_code"]
    international = "international"
    for _code in (
        "AF AL DZ AD AO AG AR AM AU AT AZ BS BH BD BB BY BE BZ BJ BT BO BA BW BR "
        "BN BG BF BI CV KH CM CA CF TD CL CN CO KM CG CR CI HR CU CY CZ KP CD DK "
        "DJ DM DO EC EG SV GQ ER EE SZ ET FJ FI FR GA GM GE DE GH GR GD GT GN GW "
        "GY HT HN HU IS IN ID IR IQ IE IL IT JM JP JO KZ KE KI KW KG LA LV LB LS "
        "LR LY LI LT LU MG MW MY MV ML MT MH MR MU MX FM MC MN ME MA MZ MM NA NR "
        "NP NL NZ NI NE NG MK NO OM PK PW PA PG PY PE PH PL PT QA KR MD RO RU RW "
        "KN LC VC WS SM ST SA SN RS SC SL SG SK SI SB SO ZA SS ES LK SD SR SE CH "
        "SY TJ TZ TH TL TG TO TT TN TR TM TV UG UA AE GB US UY UZ VU VE VN YE ZM ZW"
    ).split():
        locals()[_code] = _code

    @property
    def display_name(self):
        import pycountry

        c = pycountry.countries.get(alpha_2=self.value)
        return c.name if c else self.value.title()

    @classmethod
    def _parse(cls, v):
        vl = v.lower()
        return next(
            (m for m in cls if vl in (m.value.lower(), m.display_name.lower())), None
        ) or cls(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, *_):
        return core_schema.no_info_after_validator_function(
            cls._parse,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, *_) -> dict:
        return {"type": "string", "enum": [m.value for m in cls]}


class RecipeComplexity(CamelCaseEnum):
    VERY_EASY = auto()
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    VERY_HARD = auto()
