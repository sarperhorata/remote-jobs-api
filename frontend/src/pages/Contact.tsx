import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send, 
  MessageSquare, 
  HelpCircle, 
  Globe,
  CheckCircle,
  AlertCircle,
  Users
} from 'lucide-react';
import toast from 'react-hot-toast';
import Header from '../components/Header';
import Footer from '../components/Footer';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // SEO structured data
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "ContactPage",
    "name": "Buzz2Remote İletişim",
    "description": "Buzz2Remote ile iletişime geçin. Uzaktan çalışma fırsatları için destek alın.",
    "url": "https://buzz2remote.com/contact",
    "mainEntity": {
      "@type": "Organization",
      "name": "Buzz2Remote",
      "url": "https://buzz2remote.com",
      "logo": "https://buzz2remote.com/logo.png",
      "contactPoint": [
        {
          "@type": "ContactPoint",
          "telephone": "+90-212-555-0123",
          "contactType": "customer service",
          "areaServed": "TR",
          "availableLanguage": ["Turkish", "English"],
          "hoursAvailable": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "09:00",
            "closes": "18:00"
          }
        },
        {
          "@type": "ContactPoint",
          "email": "info@buzz2remote.com",
          "contactType": "customer service"
        },
        {
          "@type": "ContactPoint",
          "email": "support@buzz2remote.com",
          "contactType": "technical support"
        }
      ],
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "İstanbul",
        "addressCountry": "TR",
        "addressRegion": "İstanbul"
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.');
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      });
    } catch (error) {
      toast.error('Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const contactInfo = [
    {
      icon: Mail,
      title: 'Email',
      value: 'info@buzz2remote.com',
      description: 'Genel sorularınız için'
    },
    {
      icon: Phone,
      title: 'Telefon',
      value: '+90 (212) 555 0123',
      description: 'Pazartesi - Cuma, 09:00 - 18:00'
    },
    {
      icon: MapPin,
      title: 'Adres',
      value: 'İstanbul, Türkiye',
      description: 'Merkez ofis'
    },
    {
      icon: Clock,
      title: 'Çalışma Saatleri',
      value: 'Pazartesi - Cuma',
      description: '09:00 - 18:00 (GMT+3)'
    }
  ];

  const supportTopics = [
    {
      icon: HelpCircle,
      title: 'Teknik Destek',
      description: 'Platform kullanımı ile ilgili sorular',
      email: 'support@buzz2remote.com'
    },
    {
      icon: MessageSquare,
      title: 'İş Ortaklığı',
      description: 'Şirketler için işbirliği fırsatları',
      email: 'partnership@buzz2remote.com'
    },
    {
      icon: Globe,
      title: 'Medya İletişimi',
      description: 'Basın ve medya soruları',
      email: 'press@buzz2remote.com'
    }
  ];

  return (
    <>
      <Helmet>
        <title>İletişim - Buzz2Remote | Uzaktan Çalışma Fırsatları</title>
        <meta name="description" content="Buzz2Remote ile iletişime geçin. Uzaktan çalışma fırsatları, teknik destek ve iş ortaklığı için bizimle iletişime geçin. 7/24 destek." />
        <meta name="keywords" content="iletişim, uzaktan çalışma, remote job, iş fırsatları, teknik destek, Buzz2Remote" />
        <meta name="author" content="Buzz2Remote" />
        <meta name="robots" content="index, follow" />
        <meta name="language" content="tr" />
        <meta name="revisit-after" content="7 days" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://buzz2remote.com/contact" />
        <meta property="og:title" content="İletişim - Buzz2Remote | Uzaktan Çalışma Fırsatları" />
        <meta property="og:description" content="Buzz2Remote ile iletişime geçin. Uzaktan çalışma fırsatları için destek alın." />
        <meta property="og:image" content="https://buzz2remote.com/og-image.jpg" />
        <meta property="og:site_name" content="Buzz2Remote" />
        <meta property="og:locale" content="tr_TR" />
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://buzz2remote.com/contact" />
        <meta property="twitter:title" content="İletişim - Buzz2Remote | Uzaktan Çalışma Fırsatları" />
        <meta property="twitter:description" content="Buzz2Remote ile iletişime geçin. Uzaktan çalışma fırsatları için destek alın." />
        <meta property="twitter:image" content="https://buzz2remote.com/twitter-image.jpg" />
        
        {/* Canonical URL */}
        <link rel="canonical" href="https://buzz2remote.com/contact" />
        
        {/* Structured Data */}
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
        
        {/* Additional SEO Meta Tags */}
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="theme-color" content="#3B82F6" />
        <meta name="msapplication-TileColor" content="#3B82F6" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Buzz2Remote İletişim" />
        
        {/* Contact Information Schema */}
        <meta name="contact:email" content="info@buzz2remote.com" />
        <meta name="contact:phone" content="+90-212-555-0123" />
        <meta name="contact:address" content="İstanbul, Türkiye" />
        <meta name="contact:working_hours" content="Pazartesi - Cuma, 09:00 - 18:00" />
      </Helmet>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col">
        <Header />
        <main className="flex-1">
          {/* Hero Section */}
          <section className="relative py-20 overflow-hidden" role="banner" aria-label="İletişim sayfası başlığı">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
            <div className="relative container mx-auto px-4">
              <div className="text-center max-w-4xl mx-auto">
                <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
                  İletişime Geçin
                </h1>
                <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                  Sorularınız mı var? Size yardımcı olmaktan mutluluk duyarız. 
                  Aşağıdaki formu doldurun veya doğrudan bizimle iletişime geçin.
                </p>
                <div className="flex flex-wrap justify-center gap-8">
                  {[
                    { value: '50K+', label: 'Job Seekers' },
                    { value: '500+', label: 'Companies' },
                    { value: '100+', label: 'Countries' },
                    { value: '10K+', label: 'Placements' }
                  ].map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className="flex items-center justify-center w-16 h-16 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg mx-auto mb-3">
                        <Users className="w-8 h-8 text-blue-600" />
                      </div>
                      <div className="text-3xl font-bold text-gray-800">{stat.value}</div>
                      <div className="text-gray-600">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Contact Form & Info Section */}
          <section className="py-20" role="main" aria-label="İletişim formu ve bilgileri">
            <div className="container mx-auto px-4">
              <div className="grid lg:grid-cols-2 gap-12">
                {/* Contact Form */}
                <article className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl">
                  <h2 className="text-3xl font-bold text-gray-800 mb-6">Mesaj Gönderin</h2>
                  <form onSubmit={handleSubmit} className="space-y-6" role="form" aria-label="İletişim formu">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                          Ad Soyad *
                        </label>
                        <input
                          type="text"
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          required
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                        />
                      </div>
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                          Email *
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          required
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                        Konu
                      </label>
                      <input
                        type="text"
                        id="subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                      />
                    </div>
                    <div>
                      <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                        Mesajınız *
                      </label>
                      <textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        required
                        rows={5}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
                    >
                      <Send className="w-5 h-5 mr-2" />
                      {isSubmitting ? 'Gönderiliyor...' : 'Gönder'}
                    </button>
                  </form>
                </article>

                {/* Contact Info */}
                <aside className="bg-gradient-to-br from-blue-50 to-purple-100 rounded-3xl p-8 shadow-xl flex flex-col justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-6">İletişim Bilgileri</h3>
                    <ul className="space-y-6">
                      {contactInfo.map((info, idx) => (
                        <li key={idx} className="flex items-start gap-4">
                          <info.icon className="w-6 h-6 text-blue-600 mt-1" />
                          <div>
                            <div className="font-semibold text-gray-800">{info.title}</div>
                            <div className="text-gray-600">{info.value}</div>
                            <div className="text-gray-400 text-sm">{info.description}</div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-10">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Destek Konuları</h4>
                    <ul className="space-y-4">
                      {supportTopics.map((topic, idx) => (
                        <li key={idx} className="flex items-start gap-4">
                          <topic.icon className="w-5 h-5 text-purple-600 mt-1" />
                          <div>
                            <div className="font-semibold text-gray-800">{topic.title}</div>
                            <div className="text-gray-600 text-sm">{topic.description}</div>
                            <a href={`mailto:${topic.email}`} className="text-blue-600 hover:underline text-sm">{topic.email}</a>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </aside>
              </div>
            </div>
          </section>
        </main>
        <Footer />
      </div>
    </>
  );
};

export default Contact; 