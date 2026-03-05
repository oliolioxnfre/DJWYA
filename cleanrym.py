import os

def clean_duplicates(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    seen_genres = set()
    new_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip blank lines
        if not line:
            i += 1
            continue
            
        # Potentially a genre name
        genre_name = line
        # Normalize: strip and lowercase
        normalized_name = genre_name.strip().lower()
        
        # The description should be on the next line
        if i + 1 < len(lines):
            description = lines[i+1].strip()
            
            # If the next line is also blank or somehow not a description, 
            # we might have a name without description, but let's assume it is a description.
            if not description:
                # Name without description? Handle gracefully.
                if normalized_name not in seen_genres:
                    seen_genres.add(normalized_name)
                    new_content.append(genre_name + "\n")
                    new_content.append("\n")
                i += 1
                continue
            
            # We have a Name + Description block
            if normalized_name not in seen_genres:
                seen_genres.add(normalized_name)
                # Use the original genre name (but stripped) to keep the case
                new_content.append(genre_name.strip() + "\n")
                new_content.append(description + "\n")
                new_content.append("\n")
            
            i += 2
        else:
            # Last line of the file is a genre name without description
            if normalized_name not in seen_genres:
                seen_genres.add(normalized_name)
                new_content.append(genre_name.strip() + "\n")
                new_content.append("\n")
            i += 1

    with open(filepath, 'w') as f:
        f.writelines(new_content)
    
    print(f"Cleaned {filepath}. Total unique genres found: {len(seen_genres)}")

if __name__ == "__main__":
    clean_duplicates('/Users/oliverking/Antigrav/DJWYA/RYMPULL.md')
