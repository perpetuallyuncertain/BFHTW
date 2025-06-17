from BFHTW.functions.nlp.processor import nlp_processor
from BFHTW.utils.crud.crud import CRUD
from core.src.BFHTW.models.keywords import FilterModel
from BFHTW.utils.logs import get_logger

L = get_logger()

def insert_keywords():
    '''
    needs logic inserted for timer or other trigger
    
    '''

    processor = nlp_processor(
        source_table='pdf_blocks',
        save_model=FilterModel,
        assistant='BERT',
        nlp_model='ner',
        label_map_filename='label_map.json'
    )

    keywords = processor.output
    if not keywords:
        L.warning("No keywords returned from processor.")
        return


    try:
        CRUD.create_table_if_not_exists(
            table='keywords',
            model=FilterModel,
            primary_key='block_id'
        )
    except Exception as e:
        L.error(f"Error creating table {e}")

    try:
        success = CRUD.bulk_insert(
            table='keywords',
            model=FilterModel,
            data_list=keywords
        )
    except Exception as e:
        L.error(f"Failed to insert data to database with error {e}")

    L.info(f"Inserted {len(keywords)} rows into keywords db")

    if success:
        
        try:
            data_list = [(kw.block_id, {"processed": True}) for kw in keywords]

            CRUD.bulk_update(
                table='pdf_blocks',
                id_field='block_id',
                data_list=data_list
            )
            L.info(f"Updated pdf_blocks with processed tag for {len(data_list)} rows")
            return True
            
        except Exception as e:
            L.error(f"Failed to update pdf_blocks with {e}")



