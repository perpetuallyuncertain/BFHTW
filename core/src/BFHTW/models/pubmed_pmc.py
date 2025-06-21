from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated


class PMCArticleMetadata(BaseModel):
    """
    Represents metadata for a PMC full-text article that has a matched mapping
    between open-access archive files and PubMed/PMC identifiers.
    """

    ftp_path: Annotated[
        str,
        Field(description="Relative FTP path to the article tar.gz file from the PMC FTP site.")
    ]

    accession_id: Annotated[
        str,
        Field(description="PMC Accession ID, e.g. 'PMC13912'.")
    ]

    pmid_source: Annotated[
        Optional[str],
        Field(description="PMID as found in the source oa_file_list file.")
    ]

    license_type: Annotated[
        Optional[str],
        Field(description="License designation for the full-text article (e.g., CC BY, NO-CC CODE).")
    ]

    pmcid: Annotated[
        str,
        Field(description="PMCID of the article, expected to match accession_id.")
    ]

    pmid_mapped: Annotated[
        Optional[str],
        Field(description="PMID as mapped from the external PMC-ID CSV mapping file.")
    ]

    full_text_downloaded: Annotated[
        bool,
        Field(
            default=False,
            description="Marker to indicate if the document has already been processed."
            )
    ]
