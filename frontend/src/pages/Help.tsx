import React, { useState } from 'react';
import { MessageCircle, Mail, FileText, ExternalLink } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

const faqSections = {
  general: [
    {
      question: "Buzz2Remote nedir?",
      answer: "Buzz2Remote, uzaktan çalışma fırsatlarını bir araya getiren, iş arayanlar ve işverenler için özel olarak tasarlanmış bir platformdur. Türkiye'den ve dünyadan uzaktan çalışma ilanlarını bulabilir, başvurabilir ve kariyerinizi geliştirebilirsiniz."
    },
    {
      question: "Platform ücretsiz mi?",
      answer: "Evet, Buzz2Remote tamamen ücretsizdir. İş arayanlar için herhangi bir ücret talep edilmemektedir. İşverenler için ise farklı paketler sunulmaktadır."
    }
  ],
  jobSeekers: [
    {
      question: "Nasıl iş başvurusu yapabilirim?",
      answer: "Öncelikle bir hesap oluşturmanız gerekiyor. Ardından profil sayfanızdan CV'nizi yükleyebilir ve ilgilendiğiniz iş ilanlarına başvurabilirsiniz. Başvurularınızı 'Başvurularım' sayfasından takip edebilirsiniz."
    },
    {
      question: "CV'mi nasıl güncelleyebilirim?",
      answer: "Profil sayfanızdan 'CV Yükle' bölümüne giderek yeni CV'nizi yükleyebilirsiniz. CV'nizi güncel tutmanız, işverenlerin sizi daha kolay bulmasını sağlar."
    }
  ],
  employers: [
    {
      question: "İş ilanı nasıl yayınlayabilirim?",
      answer: "İşveren hesabı oluşturduktan sonra, 'İlan Yayınla' butonuna tıklayarak yeni bir ilan oluşturabilirsiniz. İlanınızı detaylı bir şekilde doldurmanız, doğru adaylara ulaşmanızı sağlar."
    },
    {
      question: "Başvuruları nasıl yönetebilirim?",
      answer: "İşveren panelinizden gelen tüm başvuruları görüntüleyebilir, adayları değerlendirebilir ve durumlarını güncelleyebilirsiniz. Adaylara geri bildirim gönderebilir ve süreçlerini takip edebilirsiniz."
    }
  ],
  technical: [
    {
      question: "Hesabıma nasıl giriş yapabilirim?",
      answer: "Ana sayfadaki 'Giriş Yap' butonuna tıklayarak e-posta ve şifrenizle giriş yapabilirsiniz. Şifrenizi unuttuysanız, 'Şifremi Unuttum' linkini kullanarak yeni şifre oluşturabilirsiniz."
    },
    {
      question: "Bildirimleri nasıl yönetebilirim?",
      answer: "Profil sayfanızdan 'Bildirim Ayarları' bölümüne giderek e-posta ve uygulama içi bildirimlerinizi özelleştirebilirsiniz."
    }
  ]
};

const Help: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>('general');
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set());

  const toggleQuestion = (question: string) => {
    const newExpanded = new Set(expandedQuestions);
    if (newExpanded.has(question)) {
      newExpanded.delete(question);
    } else {
      newExpanded.add(question);
    }
    setExpandedQuestions(newExpanded);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Yardım Merkezi
          </h1>
          <p className="mt-4 text-lg text-gray-500">
            Sıkça sorulan sorular ve platform hakkında bilmeniz gerekenler
          </p>
        </div>

        {/* Kategori Seçimi */}
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {Object.keys(faqSections).map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                activeSection === section
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {section === 'general' && 'Genel'}
              {section === 'jobSeekers' && 'İş Arayanlar'}
              {section === 'employers' && 'İşverenler'}
              {section === 'technical' && 'Teknik'}
            </button>
          ))}
        </div>

        {/* FAQ Listesi */}
        <div className="mt-8 space-y-4">
          {faqSections[activeSection as keyof typeof faqSections].map((faq: FAQItem) => (
            <div
              key={faq.question}
              className="bg-white shadow rounded-lg overflow-hidden"
            >
              <button
                onClick={() => toggleQuestion(faq.question)}
                className="w-full px-6 py-4 text-left focus:outline-none"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">
                    {faq.question}
                  </h3>
                  <svg
                    className={`h-5 w-5 text-gray-500 transform transition-transform ${
                      expandedQuestions.has(faq.question) ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </button>
              {expandedQuestions.has(faq.question) && (
                <div className="px-6 pb-4">
                  <p className="text-gray-500">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* İletişim Bölümü */}
        <div className="mt-12 bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-8">
            <h2 className="text-2xl font-bold text-gray-900">
              Hala yardıma mı ihtiyacınız var?
            </h2>
            <p className="mt-2 text-gray-500">
              Sorularınız için bize ulaşın, size yardımcı olmaktan mutluluk duyarız.
            </p>
            <div className="mt-6 space-y-4">
              <a
                href="mailto:support@buzz2remote.com"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg
                  className="mr-2 h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                E-posta Gönder
              </a>
              <div className="flex space-x-4">
                <a
                  href="https://twitter.com/buzz2remote"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Twitter</span>
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a
                  href="https://linkedin.com/company/buzz2remote"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">LinkedIn</span>
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help; 