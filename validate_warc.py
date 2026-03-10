import sys
from warcio.archiveiterator import ArchiveIterator

def validate_warc(file_path):
    print(f"--- Analyzing: {file_path} ---")
    
    count = 0
    errors = 0
    
    try:
        with open(file_path, 'rb') as stream:
            # ArchiveIterator handles both .warc and .warc.gz automatically
            for record in ArchiveIterator(stream, check_digests=True):
                try:
                    # Accessing the content forces the library to check the digest
                    record.content_stream().read()
                    
                    # Log basic info for every 100th record to show progress
                    if count % 100 == 0:
                        print(f"Processed {count} records...")
                        
                    count += 1
                except Exception as e:
                    print(f"Error in record {count} ({record.rec_type}): {e}")
                    errors += 1
                    count += 1

        print("--- Validation Complete ---")
        print(f"Total records checked: {count}")
        print(f"Integrity errors found: {errors}")
        
        return errors == 0

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"Fatal error reading WARC: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_warc.py <path_to_file.warc.gz>")
    else:
        validate_warc(sys.argv[1])