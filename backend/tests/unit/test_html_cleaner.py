import pytest
from backend.utils.html_cleaner import clean_html_tags, clean_job_data, clean_job_description


class TestHtmlCleaner:
    """HTML cleaner utility testleri"""
    
    def test_clean_html_tags_basic(self):
        """Temel HTML tag temizleme testi"""
        html_text = "<p>Bu bir <strong>test</strong> metnidir.</p>"
        expected = "Bu bir test metnidir."
        result = clean_html_tags(html_text)
        assert result == expected
    
    def test_clean_html_tags_with_entities(self):
        """HTML entities ile test"""
        html_text = "<div>Test &amp; &lt;test&gt; &quot;test&quot;</div>"
        # BeautifulSoup HTML entities'leri decode eder ama <test> tag'ini temizler
        expected = "Test & \"test\""
        result = clean_html_tags(html_text)
        assert result == expected
    
    def test_clean_html_tags_complex(self):
        """Karmaşık HTML yapısı testi"""
        html_text = """
        <div class="container">
            <h1>Başlık</h1>
            <p>Paragraf <a href="#">link</a> ve <em>italik</em> metin.</p>
            <ul>
                <li>Liste öğesi 1</li>
                <li>Liste öğesi 2</li>
            </ul>
        </div>
        """
        expected = "Başlık Paragraf link ve italik metin. Liste öğesi 1 Liste öğesi 2"
        result = clean_html_tags(html_text)
        # Fazla boşlukları normalize et
        result = " ".join(result.split())
        expected = " ".join(expected.split())
        assert result == expected
    
    def test_clean_html_tags_empty(self):
        """Boş metin testi"""
        assert clean_html_tags("") == ""
        assert clean_html_tags(None) == ""
    
    def test_clean_html_tags_no_html(self):
        """HTML olmayan metin testi"""
        text = "Bu normal bir metindir."
        result = clean_html_tags(text)
        assert result == text
    
    def test_clean_job_description_basic(self):
        """Temel job description temizleme testi"""
        description = "<p>Python Developer aranıyor. <strong>Remote</strong> çalışma.</p>"
        result = clean_job_description(description)
        expected = "Python Developer aranıyor. Remote çalışma."
        assert result == expected
    
    def test_clean_job_description_truncate(self):
        """Uzun description kısaltma testi"""
        long_text = "A" * 3000
        result = clean_job_description(long_text, max_length=100)
        assert len(result) <= 100
        assert result.endswith("...")
    
    def test_clean_job_description_with_newlines(self):
        """Satır sonları ile test"""
        description = "<p>Satır 1</p>\n<p>Satır 2</p>\n<p>Satır 3</p>"
        result = clean_job_description(description)
        expected = "Satır 1 Satır 2 Satır 3"
        assert result == expected
    
    def test_clean_job_data_dict(self):
        """Job data dictionary temizleme testi"""
        job_data = {
            "title": "<strong>Python Developer</strong>",
            "company": "<em>Tech Corp</em>",
            "description": "<p>Remote çalışma imkanı.</p>",
            "location": "İstanbul",
            "salary": "50000"
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == "Python Developer"
        assert result["company"] == "Tech Corp"
        assert result["description"] == "Remote çalışma imkanı."
        assert result["location"] == "İstanbul"
        assert result["salary"] == "50000"
    
    def test_clean_job_data_nested(self):
        """İç içe job data testi"""
        job_data = {
            "title": "<h1>Senior Developer</h1>",
            "requirements": {
                "skills": "<ul><li>Python</li><li>Django</li></ul>",
                "experience": "5+ yıl"
            }
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == "Senior Developer"
        # İç içe dictionary'ler de temizlenir
        assert result["requirements"]["skills"] == "Python Django"
        assert result["requirements"]["experience"] == "5+ yıl"
    
    def test_clean_job_data_empty_values(self):
        """Boş değerler ile test"""
        job_data = {
            "title": "",
            "description": None,
            "company": "<p></p>"
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == ""
        assert result["description"] == ""  # None değerler boş string'e çevrilir
        assert result["company"] == ""
    
    def test_clean_job_data_mixed_content(self):
        """Karışık içerik testi"""
        job_data = {
            "title": "Python Developer",
            "description": "<div>Remote çalışma. <script>alert('test')</script> Güvenli ortam.</div>",
            "benefits": "<ul><li>Sağlık sigortası</li><li>Uzaktan çalışma</li></ul>"
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == "Python Developer"
        assert "Remote çalışma" in result["description"]
        assert "alert" not in result["description"]  # Script tag temizlenmiş olmalı
        assert "Sağlık sigortası" in result["benefits"]
        assert "Uzaktan çalışma" in result["benefits"]
    
    def test_clean_job_data_special_characters(self):
        """Özel karakterler testi"""
        job_data = {
            "title": "DevOps & Cloud Engineer",
            "description": "<p>Linux & Docker & Kubernetes</p>",
            "requirements": "<ul><li>Python & JavaScript</li><li>SQL & NoSQL</li></ul>"
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == "DevOps & Cloud Engineer"
        assert "Linux & Docker & Kubernetes" in result["description"]
        assert "Python & JavaScript" in result["requirements"]
        assert "SQL & NoSQL" in result["requirements"]
    
    def test_clean_job_data_unicode(self):
        """Unicode karakterler testi"""
        job_data = {
            "title": "Türkçe Geliştirici",
            "description": "<p>İstanbul'da çalışma imkanı. Öğrenme & gelişim.</p>",
            "location": "İstanbul, Türkiye"
        }
        result = clean_job_data(job_data)
        
        assert result["title"] == "Türkçe Geliştirici"
        assert "İstanbul'da çalışma imkanı" in result["description"]
        assert result["location"] == "İstanbul, Türkiye"
    
    def test_clean_job_data_max_length(self):
        """Maksimum uzunluk testi"""
        long_description = "A" * 5000
        result = clean_job_description(long_description, max_length=100)
        
        assert len(result) <= 100
        assert result.endswith("...")
    
    def test_clean_job_data_preserve_formatting(self):
        """Format koruma testi"""
        description = """
        <h2>Pozisyon:</h2>
        <p>Python Developer</p>
        
        <h2>Gereksinimler:</h2>
        <ul>
            <li>Python 3.x</li>
            <li>Django/FastAPI</li>
        </ul>
        """
        result = clean_job_description(description)
        
        assert "Pozisyon:" in result
        assert "Python Developer" in result
        assert "Gereksinimler:" in result
        assert "Python 3.x" in result
        assert "Django/FastAPI" in result 