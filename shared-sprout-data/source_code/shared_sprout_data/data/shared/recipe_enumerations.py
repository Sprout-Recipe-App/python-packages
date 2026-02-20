from enum import Enum, auto

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class TitleCaseEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.replace("_", " ").title()

    @classmethod
    def _from_string(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            return next((m for m in cls if m.value.lower() == value.lower()), cls(value))

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._from_string,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.value),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> dict:
        return {"type": "string", "enum": [m.value for m in cls]}


class DietType(TitleCaseEnum):
    ANY = auto()
    PESCATARIAN = auto()
    VEGETARIAN = auto()
    VEGAN = auto()
    RAW = auto()


class DishType(TitleCaseEnum):
    APPETIZER = auto()
    ENTREE = auto()
    SIDE_DISH = auto()
    DESSERT = auto()
    BEVERAGE = auto()
    SNACK = auto()
    CONDIMENT = auto()


class Cuisine(TitleCaseEnum):
    INTERNATIONAL = auto()
    AFGHAN = auto()
    ALBANIAN = auto()
    ALGERIAN = auto()
    ANDORRAN = auto()
    ANGOLAN = auto()
    ANTIGUAN = auto()
    ARGENTINIAN = auto()
    ARMENIAN = auto()
    AUSTRALIAN = auto()
    AUSTRIAN = auto()
    AZERBAIJANI = auto()
    BAHAMIAN = auto()
    BAHRAINI = auto()
    BANGLADESHI = auto()
    BARBADIAN = auto()
    BELARUSIAN = auto()
    BELGIAN = auto()
    BELIZEAN = auto()
    BENINESE = auto()
    BHUTANESE = auto()
    BOLIVIAN = auto()
    BOSNIAN = auto()
    BOTSWANAN = auto()
    BRAZILIAN = auto()
    BRUNEIAN = auto()
    BULGARIAN = auto()
    BURKINABE = auto()
    BURUNDIAN = auto()
    CAPE_VERDEAN = auto()
    CAMBODIAN = auto()
    CAMEROONIAN = auto()
    CANADIAN = auto()
    CENTRAL_AFRICAN = auto()
    CHADIAN = auto()
    CHILEAN = auto()
    CHINESE = auto()
    COLOMBIAN = auto()
    COMORIAN = auto()
    COSTA_RICAN = auto()
    IVORIAN = auto()
    CROATIAN = auto()
    CUBAN = auto()
    CYPRIOT = auto()
    CZECH = auto()
    NORTH_KOREAN = auto()
    DANISH = auto()
    DJIBOUTIAN = auto()
    ECUADORIAN = auto()
    EGYPTIAN = auto()
    SALVADORAN = auto()
    EQUATOGUINEAN = auto()
    ERITREAN = auto()
    ESTONIAN = auto()
    SWAZI = auto()
    ETHIOPIAN = auto()
    FIJIAN = auto()
    FINNISH = auto()
    FRENCH = auto()
    GABONESE = auto()
    GAMBIAN = auto()
    GEORGIAN = auto()
    GERMAN = auto()
    GHANAIAN = auto()
    GREEK = auto()
    GRENADIAN = auto()
    GUATEMALAN = auto()
    GUINEAN = auto()
    GUYANESE = auto()
    HAITIAN = auto()
    HONDURAN = auto()
    HUNGARIAN = auto()
    ICELANDIC = auto()
    INDIAN = auto()
    INDONESIAN = auto()
    IRANIAN = auto()
    IRAQI = auto()
    IRISH = auto()
    ISRAELI = auto()
    ITALIAN = auto()
    JAMAICAN = auto()
    JAPANESE = auto()
    JORDANIAN = auto()
    KAZAKHSTANI = auto()
    KENYAN = auto()
    KUWAITI = auto()
    KYRGYZSTANI = auto()
    LAO = auto()
    LATVIAN = auto()
    LEBANESE = auto()
    BASOTHO = auto()
    LIBERIAN = auto()
    LIBYAN = auto()
    LIECHTENSTEINER = auto()
    LITHUANIAN = auto()
    LUXEMBOURGISH = auto()
    MALAGASY = auto()
    MALAWIAN = auto()
    MALAYSIAN = auto()
    MALDIVIAN = auto()
    MALIAN = auto()
    MALTESE = auto()
    MARSHALLESE = auto()
    MAURITANIAN = auto()
    MAURITIAN = auto()
    MEXICAN = auto()
    MICRONESIAN = auto()
    MONEGASQUE = auto()
    MONGOLIAN = auto()
    MONTENEGRIN = auto()
    MOROCCAN = auto()
    MOZAMBICAN = auto()
    MYANMAR = auto()
    NAMIBIAN = auto()
    NAURUAN = auto()
    NEPALI = auto()
    DUTCH = auto()
    NEW_ZEALANDER = auto()
    NICARAGUAN = auto()
    NIGERIEN = auto()
    NIGERIAN = auto()
    MACEDONIAN = auto()
    NORWEGIAN = auto()
    OMANI = auto()
    PAKISTANI = auto()
    PALAUAN = auto()
    PANAMANIAN = auto()
    PAPUA_NEW_GUINEAN = auto()
    PARAGUAYAN = auto()
    PERUVIAN = auto()
    FILIPINO = auto()
    POLISH = auto()
    PORTUGUESE = auto()
    QATARI = auto()
    SOUTH_KOREAN = auto()
    MOLDOVAN = auto()
    ROMANIAN = auto()
    RUSSIAN = auto()
    RWANDAN = auto()
    KITTITIAN = auto()
    SAINT_LUCIAN = auto()
    VINCENTIAN = auto()
    SAMOAN = auto()
    SAMMARINESE = auto()
    SAO_TOMEAN = auto()
    SAUDI = auto()
    SENEGALESE = auto()
    SERBIAN = auto()
    SEYCHELLOIS = auto()
    SIERRA_LEONEAN = auto()
    SINGAPOREAN = auto()
    SLOVAK = auto()
    SLOVENIAN = auto()
    SOLOMON_ISLANDER = auto()
    SOMALI = auto()
    SOUTH_AFRICAN = auto()
    SOUTH_SUDANESE = auto()
    SPANISH = auto()
    SRI_LANKAN = auto()
    SUDANESE = auto()
    SURINAMESE = auto()
    SWEDISH = auto()
    SWISS = auto()
    SYRIAN = auto()
    TAJIKISTANI = auto()
    TANZANIAN = auto()
    THAI = auto()
    TIMORESE = auto()
    TOGOLESE = auto()
    TONGAN = auto()
    TRINIDADIAN = auto()
    TUNISIAN = auto()
    TURKISH = auto()
    TURKMEN = auto()
    TUVALUAN = auto()
    UGANDAN = auto()
    UKRAINIAN = auto()
    EMIRATI = auto()
    BRITISH = auto()
    AMERICAN = auto()
    URUGUAYAN = auto()
    UZBEKISTANI = auto()
    VENEZUELAN = auto()
    VIETNAMESE = auto()
    YEMENI = auto()
    ZAMBIAN = auto()
    ZIMBABWEAN = auto()
    CONGOLESE_BRAZZAVILLE = "Congolese (Congo-Brazzaville)"
    CONGOLESE_KINSHASA = "Congolese (Congo-Kinshasa)"
    DOMINICAN_DOMINICA = "Dominican (Dominica)"
    DOMINICAN_DOMINICAN_REPUBLIC = "Dominican (Dominican Republic)"
    BISSAU_GUINEAN = "Bissau-Guinean"
    I_KIRIBATI = "I-Kiribati"
    NI_VANUATU = "Ni-Vanuatu"


class RecipeComplexity(str, Enum):
    VERY_EASY = "veryEasy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "veryHard"

    @property
    def level(self) -> int:
        return list(RecipeComplexity).index(self) + 1

    @classmethod
    def _from_level(cls, level: int):
        members = list(cls)
        return members[min(max(level - 1, 0), len(members) - 1)]

    @classmethod
    def _from_string(cls, value: str):
        return next((m for m in cls if m.value == value), cls.MEDIUM)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls._from_string,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.value),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> dict:
        return {"type": "string", "enum": [m.value for m in cls]}

    def __str__(self):
        return self.name.replace("_", " ").title()
