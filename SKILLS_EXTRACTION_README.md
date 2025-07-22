# 🎯 CV Skills Extraction Özelliği

Buzz2Remote platformuna eklenen yeni **AI destekli CV Skills Extraction** özelliği, kullanıcıların CV'lerinden otomatik olarak becerilerini çıkarıp tag olarak kullanmalarını sağlar.

## ✨ Özellikler

### 🔍 Otomatik Skills Extraction
- **AI Destekli Analiz**: OpenAI GPT-4 ile gelişmiş skills extraction
- **Pattern Matching**: Fallback olarak pattern matching algoritması
- **Kategori Bazlı Sınıflandırma**: Technical, Soft Skills, Languages, Tools, Certifications
- **Confidence Scoring**: Her skill için güven skoru (0-100%)

### 🏷️ Skills Kategorileri

#### Technical Skills
- **Programming Languages**: Python, JavaScript, Java, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala, R, MATLAB
- **Frameworks**: React, Angular, Vue, Svelte, Node.js, Express, Django, Flask, Spring, ASP.NET, Laravel, Rails, FastAPI
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch, SQLite, Oracle, SQL Server, Cassandra, DynamoDB
- **Cloud Platforms**: AWS, Azure, GCP, Google Cloud, Heroku, DigitalOcean, Vercel, Netlify, Firebase
- **DevOps Tools**: Docker, Kubernetes, Jenkins, Travis CI, CircleCI, GitHub Actions, Terraform, Ansible, GitLab CI
- **Version Control**: Git, GitHub, GitLab, Bitbucket, SVN
- **API Technologies**: REST, GraphQL, gRPC, WebSockets, SOAP, API
- **Architecture**: Microservices, Serverless, Monolith, Event-Driven, Domain-Driven Design
- **Methodologies**: CI/CD, DevOps, Agile, Scrum, Kanban, TDD, BDD, Lean

#### Soft Skills
- Leadership, Communication, Teamwork, Problem Solving, Critical Thinking
- Time Management, Adaptability, Creativity, Emotional Intelligence, Negotiation
- Project Management, Customer Service, Analytical Thinking, Strategic Planning

#### Languages
- English, Turkish, German, French, Spanish, Italian, Portuguese
- Russian, Chinese, Japanese, Korean, Arabic, Dutch, Swedish, Norwegian

## 🚀 Kullanım

### 1. CV Yükleme
1. Profile sayfasına gidin
2. "CV / Resume" bölümünde CV'nizi yükleyin
3. CV yüklendikten sonra otomatik olarak skills extraction başlar

### 2. Skills Extraction
1. CV yüklendikten sonra "Extract Skills from CV" butonuna tıklayın
2. AI analiz süreci başlar (birkaç saniye sürer)
3. Çıkarılan skills kategorilere göre gösterilir

### 3. Skills Yönetimi
- **Edit Skills**: Skills'leri düzenlemek için
- **Add New Skill**: Yeni skill eklemek için
- **Remove Skills**: Skills'leri kaldırmak için
- **Save Changes**: Değişiklikleri kaydetmek için

### 4. Skills Kaynakları
- **📄 CV**: CV'den otomatik çıkarılan skills
- **🤖 AI Enhanced**: AI ile geliştirilmiş skills
- **✏️ Manual**: Manuel olarak eklenen skills

## 🔧 Teknik Detaylar

### Backend API Endpoints

#### Skills Extraction
```http
POST /api/v1/skills/extract-from-cv
Authorization: Bearer <token>
```

#### Skills Management
```http
GET /api/v1/skills/user-skills
PUT /api/v1/skills/update-skills
GET /api/v1/skills/suggestions?query=<skill_name>
```

#### File Upload
```http
POST /api/v1/skills/extract-from-file
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

### Frontend Components

#### SkillsExtraction Component
```typescript
interface Skill {
  id: string;
  name: string;
  category?: string;
  confidence?: number;
  source: 'cv' | 'manual' | 'ai';
}

interface SkillsExtractionProps {
  skills: Skill[];
  onSkillsUpdate: (skills: Skill[]) => void;
  isExtracting?: boolean;
  className?: string;
}
```

### AI Integration
- **Model**: OpenAI GPT-4o-mini
- **Prompt Engineering**: Özelleştirilmiş CV analiz prompt'u
- **Fallback**: Pattern matching algoritması
- **Confidence Scoring**: Context-based confidence hesaplama

## 📊 Veri Yapısı

### Skills Object
```json
{
  "id": "skill-1",
  "name": "React",
  "category": "technical",
  "confidence": 95,
  "source": "ai"
}
```

### Extraction Result
```json
{
  "skills": [...],
  "summary": {
    "total_skills": 15,
    "technical_count": 8,
    "soft_count": 4,
    "languages_count": 2,
    "tools_count": 1,
    "certifications_count": 0
  },
  "extraction_method": "ai_enhanced",
  "confidence_score": 87.5,
  "extracted_at": "2024-01-15T10:30:00Z"
}
```

## 🎨 UI/UX Özellikleri

### Visual Design
- **Category Colors**: Her kategori için farklı renkler
- **Source Icons**: Skills kaynağını gösteren ikonlar
- **Confidence Indicators**: Düşük güven skorları için uyarılar
- **Loading States**: Extraction sırasında animasyonlar

### User Experience
- **Drag & Drop**: Kolay CV yükleme
- **Real-time Feedback**: Anlık bildirimler
- **Edit Mode**: Kolay skills düzenleme
- **Keyboard Support**: Enter tuşu ile skill ekleme

## 🔒 Güvenlik

### Premium Gating
- AI CV analizi sadece premium kullanıcılar için
- Basic pattern matching tüm kullanıcılar için
- Subscription kontrolü backend'de

### Data Privacy
- CV içeriği sadece skills extraction için kullanılır
- OpenAI API'ye gönderilen veriler şifrelenir
- Kullanıcı verileri güvenli şekilde saklanır

## 🧪 Test Coverage

### Frontend Tests
- Component rendering
- User interactions
- State management
- Error handling
- Loading states

### Backend Tests
- API endpoints
- Skills extraction logic
- AI integration
- Error handling
- Data validation

## 🚀 Gelecek Geliştirmeler

### Planlanan Özellikler
- **Skill Recommendations**: AI destekli skill önerileri
- **Skill Matching**: Job ilanları ile skill eşleştirme
- **Skill Trends**: Sektör trendlerine göre skill analizi
- **Skill Validation**: Skills doğrulama sistemi
- **Bulk Import**: Toplu skills import

### Teknik İyileştirmeler
- **Caching**: Skills extraction sonuçları cache'leme
- **Batch Processing**: Toplu CV işleme
- **Advanced NLP**: Daha gelişmiş doğal dil işleme
- **Multi-language Support**: Çoklu dil desteği

## 📝 Kullanım Örnekleri

### CV Upload ve Skills Extraction
```javascript
// CV yükleme
const handleCvUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/v1/profile/upload-cv', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  // Otomatik skills extraction
  setTimeout(() => extractSkillsFromCV(), 1000);
};

// Skills extraction
const extractSkillsFromCV = async () => {
  const response = await fetch('/api/v1/skills/extract-from-cv', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const result = await response.json();
  setUserSkills(result.data.skills);
};
```

### Skills Management
```javascript
// Skills güncelleme
const updateUserSkills = async (skills) => {
  const response = await fetch('/api/v1/skills/update-skills', {
    method: 'PUT',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      skills: skills.map(skill => skill.name),
      extracted_skills: skills
    })
  });
};
```

## 🤝 Katkıda Bulunma

Bu özelliği geliştirmek için:

1. **Issues**: Bug'ları ve özellik isteklerini bildirin
2. **Pull Requests**: Kod katkıları yapın
3. **Documentation**: Dokümantasyonu geliştirin
4. **Testing**: Test coverage'ı artırın

## 📞 Destek

Herhangi bir sorun yaşarsanız:
- **GitHub Issues**: Teknik sorunlar için
- **Email**: genel sorular için
- **Documentation**: Detaylı kullanım kılavuzu için

---

**Not**: Bu özellik premium kullanıcılar için AI destekli analiz sunar. Basic kullanıcılar pattern matching ile sınırlıdır. 