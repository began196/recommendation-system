def extract_maker(soup):
    # Find all <p> tags
    p_tags = soup.find_all('p')
    
    for p_tag in p_tags:
        if 'Maker:' in p_tag.get_text():  # Check if "Maker:" is part of the text
            # If it contains an <a> tag, get the text of the <a>
            link_tag = p_tag.find('a')
            if link_tag:
                return link_tag.text.strip()
            # Otherwise, return the text after "Maker:"
            return p_tag.get_text().replace('Maker:', '').strip()
    
    return None  # Return None if no "Maker:" is found