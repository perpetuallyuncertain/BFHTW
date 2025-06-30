from typing import Optional, Annotated
from pydantic import Field

#----------------------------------------------------------------------------------------------------------
# Block model for NXML parsing, inherits from Block Base
'''
This model denotes the required fields to populate a block extracted from an NXMl file that facilitates
population of the document database
'''

from BFHTW.models.block_model import BlockBase

class NXMLBlock(BlockBase):
    """
    Extended block model for NXML-specific attributes.

    Focuses on structured content with section semantics, omitting layout or visual metadata.
    """

    figure_id: Annotated[
        Optional[str],
        Field(default=None, description="ID of associated figure if the block describes a figure")
    ]

    table_id: Annotated[
        Optional[str],
        Field(default=None, description="ID of associated table if the block describes a table")
    ]

    caption_type: Annotated[
        Optional[str],
        Field(default=None, description="Type of caption (e.g., figure, table)")
    ]

    caption_title: Annotated[
        Optional[str],
        Field(default=None, description="Title or label of the captioned item")
    ]

    class Config(BlockBase.Config):
        json_schema_extra = {
            "example": {
                "figure_id": None,
                "table_id": None,
                "caption_type": None,
                "caption_title": None,
                # Include shared base fields too if desired
                "block_id": "abc",
                "doc_id": "xyz",
                "text": "Some text...",
            }
        }
#----------------------------------------------------------------------------------------------------------
# Meta model for NXML parsing, inherits from Block Base
'''
This model denotes the required fields to populate the metadata extracted from an NXMl file that facilitates
population of the document database
'''
from BFHTW.models.meta_model import MetaBase

class NXMLMetadata(MetaBase):
    """
    Extended metadata model with NXML-specific fields, inheriting shared fields from MetaBase.
    """

    external_id: Annotated[
        Optional[str],
        Field(default=None, description="Primary external ID, such as PMC ID, manuscript ID, etc.")
    ]

    doi: Annotated[
        Optional[str],
        Field(default=None, description="Digital Object Identifier")
    ]

    journal: Annotated[
        Optional[str],
        Field(default=None, description="Name of the journal")
    ]

    publication_date: Annotated[
        Optional[str],
        Field(default=None, description="Publication date in YYYY-MM-DD format if available")
    ]

    open_access: Annotated[
        Optional[bool],
        Field(default=None, description="True if the article is designated open access")
    ]

    class Config(MetaBase.Config):
        json_schema_extra = {
            "example": {
                "external_id": "PMC7654321",
                "doi": "10.1016/j.jhep.2021.04.019",
                "journal": "Journal of Hepatology",
                "publication_date": "2021-09-01",
                "open_access": True
            }
        }
