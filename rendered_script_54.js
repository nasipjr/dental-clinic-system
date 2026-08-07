
    (function() {
      function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
      }
      const themeCookie = getCookie('theme');
      const savedTheme = themeCookie || localStorage.getItem('theme') || 'light';
      document.documentElement.setAttribute('data-bs-theme', savedTheme);
      localStorage.setItem('theme', savedTheme);
      
      const currentLang = getCookie('lang') || 'en' || 'en';
      localStorage.setItem('lang', currentLang);
    })();
  