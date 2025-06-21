from .BFHTW.models.pdf_extraction import PDFMetadata

class ResponseModel(PDFMetadata):
    @classmethod
    def null_response(cls) -> 'ResponseModel':
        '''Return a null response instance with default values.'''
        return cls(
            doc_id='',
            format='Unknown',
            title='No title available',
            author='No author available',
            subject=None,
            keywords=[],
            creator='Unknown',
            producer='Unknown',
            creationDate=None,
            modDate=None,
            trapped=False,
            encryption=None
        )
    
    @classmethod
    def from_content(cls, content: str, **kwargs) -> 'ResponseModel':
        """
        Creates a ResponseModel from content and optional keyword fields.
        Falls back to null_response if content is empty or whitespace.
        """
        if not content.strip():
            return cls.null_response()
        return cls(**kwargs)
