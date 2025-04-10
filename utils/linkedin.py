import requests
from bs4 import BeautifulSoup

def fetch_linkedin_data(linkedin_url):
    """
    LinkedIn URL'sinden kullanıcı verilerini çeker.
    """
    try:
        response = requests.get(linkedin_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Örnek olarak, LinkedIn profilindeki isim ve başlık bilgilerini çekelim
        name = soup.find('h1', class_='text-heading-xlarge').text.strip()
        title = soup.find('div', class_='text-body-medium').text.strip()
        
        return {
            'name': name,
            'title': title,
        }
    except Exception as e:
        print(f"Error fetching LinkedIn data: {e}")
        return None 