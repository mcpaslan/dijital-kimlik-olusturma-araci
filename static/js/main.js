/**
 * Dijital İmza Aracı — JavaScript
 * İnteraktif Animasyonlar & UI Kontrolleri (Masihullah Omar Referanslı)
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Yardım Modalı Kontrolü
    initHelpModal();

    // 2. Scroll Reveal / Fade-up Animasyonu (Intersection Observer)
    initScrollReveal();

    // 3. İnteraktif Partikül Ağı Arka Planı (Canvas Particles)
    initParticleNetwork();

    // 4. Dinamik Klavye Yazı Animasyonu (Hero Section)
    initTypingEffect();

    // 5. Giriş Sinematik Animasyonu (Intro Overlay)
    initIntroOverlay();

    // 6. Kriptografik İşlem Konsol Overlay (Form Submit preloader)
    initCryptoProgressOverlay();

    // 7. Modern Sürükle Bırak Dosya Yükleme Alanları
    initDragDropZones();

    // 8. Canlı Kriptografik Hash Önizlemesi
    initLiveHashPreview();
});

/* ========================================================
 * 1. YARDIM MODALI
 * ======================================================== */
function initHelpModal() {
    const helpShown = localStorage.getItem('helpModalShown');
    if (!helpShown) {
        const modal = document.getElementById('helpModal');
        if (modal) {
            setTimeout(() => {
                modal.classList.add('show');
            }, 600);
        }
    }
}

function closeHelpModal() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.classList.remove('show');
        localStorage.setItem('helpModalShown', 'true');
    }
}

// Modal dışına tıklanınca kapat
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        closeHelpModal();
    }
});

/* ========================================================
 * 2. SCROLL REVEAL (FADE-UP ANIMATION)
 * ======================================================== */
function initScrollReveal() {
    const fadeElements = document.querySelectorAll('.fade-up');
    
    const observerOptions = {
        root: null,
        threshold: 0.05,
        rootMargin: '0px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Hafif ardışık gecikme (stagger effect) eklemek için
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    fadeElements.forEach(el => {
        observer.observe(el);
    });
}

/* ========================================================
 * 3. INTERAKTIF PARTIKÜL AĞI (CANVAS PARTICLES)
 * ======================================================== */
function initParticleNetwork() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    
    // Pencere boyutuna göre ayarla
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Mouse Pozisyonu
    const mouse = {
        x: null,
        y: null,
        radius: 120 // Etkileşim yarıçapı
    };

    window.addEventListener('mousemove', function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseout', function() {
        mouse.x = null;
        mouse.y = null;
    });

    // Partikül Sınıfı
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.radius = Math.random() * 2 + 1.5;
            this.color = 'rgba(79, 70, 229, 0.15)'; // Indigo soft color
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }

        update() {
            // Sınırlardan sekme
            if (this.x < 0 || this.x > canvas.width) this.vx = -this.vx;
            if (this.y < 0 || this.y > canvas.height) this.vy = -this.vy;

            // Hareket et
            this.x += this.vx;
            this.y += this.vy;

            // Mouse Etkileşimi (İtme/Çekme)
            if (mouse.x != null && mouse.y != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.hypot(dx, dy);
                if (distance < mouse.radius) {
                    // Mouse'a göre hafifçe it
                    const force = (mouse.radius - distance) / mouse.radius;
                    this.x -= (dx / distance) * force * 1.5;
                    this.y -= (dy / distance) * force * 1.5;
                }
            }
        }
    }

    // Partikülleri oluştur
    const density = Math.floor((canvas.width * canvas.height) / 11000);
    const particleCount = Math.min(Math.max(density, 40), 120); // Ekran genişliğine göre dinamik adet
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // Çizgileri çiz
    function connectParticles() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.hypot(dx, dy);

                if (distance < 110) {
                    // Mesafeye göre opasiteyi azalt
                    const opacity = (1 - (distance / 110)) * 0.12;
                    ctx.strokeStyle = `rgba(79, 70, 229, ${opacity})`;
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    // Animasyon Döngüsü
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(p => {
            p.update();
            p.draw();
        });

        connectParticles();
        animationId = requestAnimationFrame(animate);
    }
    animate();
}

/* ========================================================
 * 4. DİNAMİK KLAVYE YAZI EFEKTİ
 * ======================================================== */
function initTypingEffect() {
    const element = document.getElementById('typing-text');
    if (!element) return;

    const words = [
        "RSA ile Güvenceye Alın",
        "Ed25519 ile Hızlandırın",
        "X.509 Sertifikalarıyla Doğrulayın",
        "Dosyalarınızı Kolayca İmzalayın"
    ];
    
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 75;

    function type() {
        const currentWord = words[wordIndex];
        
        if (isDeleting) {
            element.textContent = currentWord.substring(0, charIndex - 1);
            charIndex--;
            typingSpeed = 30; // Silme hızı daha hızlı
        } else {
            element.textContent = currentWord.substring(0, charIndex + 1);
            charIndex++;
            typingSpeed = 80; // Yazma hızı normal
        }

        // Kelime bittiğinde
        if (!isDeleting && charIndex === currentWord.length) {
            isDeleting = true;
            typingSpeed = 1800; // Kelimeyi okumak için bekleme süresi
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            typingSpeed = 300; // Sonraki kelimeye geçiş beklemesi
        }

        setTimeout(type, typingSpeed);
    }

    // Animasyonu başlat
    setTimeout(type, 800);
}

/* ========================================================
 * 5. CİNEMATİK INTRO OVERLAY (PRELOADER)
 * ======================================================== */
function initIntroOverlay() {
    const overlay = document.getElementById('intro-overlay');
    if (!overlay) return;

    // Yalnızca ilk giriş (sessionStorage'da yoksa) VEYA sayfa yenilendiğinde (reload) göster
    const navigationEntry = performance.getEntriesByType('navigation')[0];
    const isReload = navigationEntry && navigationEntry.type === 'reload';
    const isFirstTime = !sessionStorage.getItem('intro_shown');

    if (!isFirstTime && !isReload) {
        overlay.style.display = 'none';
        document.body.style.overflow = '';
        return;
    }

    // İlk gösterim yapıldı olarak kaydet
    sessionStorage.setItem('intro_shown', 'true');

    // Intro açıkken sayfa kaydırmasını engelle
    document.body.style.overflow = 'hidden';

    // Girişi kapatma tetikleyicisi
    function dismissIntro() {
        if (overlay.classList.contains('dismissed')) return;
        
        overlay.classList.add('dismissed');
        
        // Sayfa kaydırmasını tekrar aç
        document.body.style.overflow = '';
        
        // 1 saniyelik yukarı kayma animasyonundan sonra DOM'dan gizle
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 1000);
    }

    // Otomatik kapanış (3.5 saniye)
    const autoDismiss = setTimeout(dismissIntro, 3500);

    // Kullanıcı etkileşimi ile anında kapatma
    overlay.addEventListener('click', () => {
        clearTimeout(autoDismiss);
        dismissIntro();
    });

    // Klavye tuşuyla kapatma
    window.addEventListener('keydown', function(e) {
        if (!overlay.classList.contains('dismissed')) {
            clearTimeout(autoDismiss);
            dismissIntro();
        }
    });

    // Kaydırma (Scroll/Wheel) hareketiyle kapatma
    window.addEventListener('wheel', function(e) {
        if (!overlay.classList.contains('dismissed') && Math.abs(e.deltaY) > 5) {
            clearTimeout(autoDismiss);
            dismissIntro();
        }
    }, { passive: true });

    window.addEventListener('touchmove', function(e) {
        if (!overlay.classList.contains('dismissed')) {
            clearTimeout(autoDismiss);
            dismissIntro();
        }
    }, { passive: true });
}

/* ========================================================
 * 6. KRİPTOGRAFİK İŞLEM KONSOL OVERLAY (PROGRESS TERMINAL)
 * ======================================================== */
function initCryptoProgressOverlay() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // İndirme işlemlerini atla (animasyon gösterilmeyecek)
            const action = form.getAttribute('action') || '';
            if (action.includes('download') || action.includes('download_key') || action.includes('download_sig')) {
                return; // Normal form gönderimine izin ver
            }

            if (form.dataset.submitting === 'true') return;
            
            e.preventDefault();
            
            let title = "İŞLEM GERÇEKLEŞTİRİLİYOR";
            let themeClass = "verify-theme";
            const path = window.location.pathname;

            if (path.includes('generate') || action.includes('generate')) {
                title = "Anahtarlar Eşleştiriliyor";
                themeClass = "keygen-theme";
            } else if (path.includes('create') || action.includes('create')) {
                title = "Sertifika Mühürleniyor";
                themeClass = "cert-theme";
            } else if (path.includes('sign') || action.includes('sign')) {
                title = "Dijital İmza Atılıyor";
                themeClass = "sign-theme";
            } else if (path.includes('verify') || action.includes('verify')) {
                title = "İmza Doğrulanıyor";
                themeClass = "verify-theme";
            } else {
                form.dataset.submitting = 'true';
                form.submit();
                return;
            }

            const card = form.closest('.card') || form.parentElement;
            if (!card) {
                form.dataset.submitting = 'true';
                form.submit();
                return;
            }

            const overlay = document.createElement('div');
            overlay.className = `crypto-progress-overlay ${themeClass}`;
            
            let animHtml = '';
            if (themeClass === 'keygen-theme') {
                animHtml = `
                    <svg class="minimal-svg keygen-svg" viewBox="0 0 100 100">
                        <circle class="ring-pub" cx="40" cy="50" r="22" />
                        <circle class="ring-priv" cx="60" cy="50" r="22" />
                    </svg>
                `;
            } else if (themeClass === 'cert-theme') {
                animHtml = `
                    <svg class="minimal-svg cert-svg" viewBox="0 0 100 100">
                        <rect class="doc-border" x="25" y="15" width="50" height="70" rx="4" />
                        <line class="doc-line line-1" x1="35" y1="30" x2="65" y2="30" />
                        <line class="doc-line line-2" x1="35" y1="45" x2="65" y2="45" />
                        <path class="doc-sign" d="M35,65 Q45,55 55,65 T70,60" />
                    </svg>
                `;
            } else if (themeClass === 'sign-theme') {
                animHtml = `
                    <svg class="minimal-svg sign-svg" viewBox="0 0 120 60">
                        <path class="sign-wave" d="M10,30 Q30,10 50,30 T90,30 T110,30" />
                    </svg>
                `;
            } else if (themeClass === 'verify-theme') {
                animHtml = `
                    <div class="scanner-container">
                        <div class="scanner-line"></div>
                        <svg class="minimal-svg verify-svg" viewBox="0 0 100 100">
                            <polygon class="shield-path" points="50,15 80,25 80,55 50,85 20,55 20,25" />
                        </svg>
                    </div>
                `;
            }

            overlay.innerHTML = `
                <div class="minimal-animation-container">
                    ${animHtml}
                    <div class="minimal-anim-title">${title}...</div>
                </div>
            `;
            
            card.style.position = 'relative';
            card.appendChild(overlay);

            // 1.8 saniye boyunca işlem animasyonunu oynat, ardından yumuşakça sönümlenip formu gönder
            setTimeout(() => {
                overlay.classList.add('fade-out');
                setTimeout(() => {
                    form.dataset.submitting = 'true';
                    form.submit();
                }, 400);
            }, 1800);
        });
    });
}

/* ========================================================
 * 7. MODERN DRAG & DROP FILE UPLOAD INITIALIZER
 * ======================================================== */
function initDragDropZones() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    // Tarayıcı varsayılan sürükle bırak olaylarını devre dışı bırak
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    fileInputs.forEach(input => {
        if (input.dataset.dragDropInit === 'true') return;
        input.dataset.dragDropInit = 'true';

        // Dosya input'unu gizle
        input.style.display = 'none';

        // Temayı belirle (url veya form action'a göre)
        let themeClass = 'theme-purple'; // varsayılan
        const path = window.location.pathname;
        if (path.includes('verify')) {
            themeClass = 'theme-green';
        } else if (path.includes('create') || path.includes('certificate')) {
            themeClass = 'theme-cyan';
        } else if (path.includes('generate') || path.includes('key')) {
            themeClass = 'theme-amber';
        }

        // Drag Drop Zone HTML oluştur
        const zone = document.createElement('div');
        zone.className = `drag-drop-zone ${themeClass}`;
        
        // Kabul edilen dosya uzantısını göster
        const acceptAttr = input.getAttribute('accept') || '';
        let subtext = 'Herhangi bir dosya yüklenebilir';
        let acceptIcon = '📂';
        
        if (input.id === 'cert_file' || input.name === 'cert_file') {
            subtext = 'Yalnızca sertifika dosyaları (.pem)';
            acceptIcon = '📜';
        } else if (acceptAttr.includes('.pem')) {
            subtext = 'Yalnızca .pem dosyaları';
            acceptIcon = '🔑';
        } else if (acceptAttr.includes('.sig')) {
            subtext = 'Yalnızca .sig imza dosyaları';
            acceptIcon = '🛡️';
        }

        zone.innerHTML = `
            <div class="dd-content">
                <span class="dd-icon">${acceptIcon}</span>
                <div class="dd-text">Dosyayı sürükleyin veya <span>göz atın</span></div>
                <div class="dd-subtext">${subtext}</div>
            </div>
            <div class="dd-file-info" style="display: none;">
                <span class="dd-file-icon">📄</span>
                <span class="dd-file-name"></span>
                <span class="dd-file-size"></span>
                <button type="button" class="dd-remove-btn" title="Dosyayı Kaldır">✕</button>
            </div>
        `;

        // Input'un hemen arkasına yerleştir
        input.parentNode.insertBefore(zone, input.nextSibling);

        const ddContent = zone.querySelector('.dd-content');
        const ddFileInfo = zone.querySelector('.dd-file-info');
        const fileNameSpan = zone.querySelector('.dd-file-name');
        const fileSizeSpan = zone.querySelector('.dd-file-size');
        const removeBtn = zone.querySelector('.dd-remove-btn');

        // Tıklama ile dosya seçiciyi aç
        zone.addEventListener('click', (e) => {
            if (e.target.closest('.dd-remove-btn')) return;
            input.click();
        });

        // Dosya seçildiğinde arayüzü güncelle
        input.addEventListener('change', () => {
            updateFileInfo(input.files[0]);
        });

        // Sürükleme olayları
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, () => {
                zone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, () => {
                zone.classList.remove('dragover');
            }, false);
        });

        zone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length) {
                input.files = files; // Dosyayı gizli input'a ata
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        }, false);

        // Dosyayı temizleme butonu
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            input.value = ''; // Input'u sıfırla
            ddFileInfo.style.display = 'none';
            ddContent.style.display = 'flex';
            
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        });

        function updateFileInfo(file) {
            if (file) {
                fileNameSpan.textContent = file.name;
                
                let sizeStr = '';
                const bytes = file.size;
                if (bytes < 1024) sizeStr = `${bytes} B`;
                else if (bytes < 1048576) sizeStr = `${(bytes / 1024).toFixed(1)} KB`;
                else sizeStr = `${(bytes / 1048576).toFixed(1)} MB`;
                
                fileSizeSpan.textContent = `(${sizeStr})`;
                
                ddContent.style.display = 'none';
                ddFileInfo.style.display = 'flex';
            } else {
                ddFileInfo.style.display = 'none';
                ddContent.style.display = 'flex';
            }
        }
    });
}

/* ========================================================
 * 8. CANLI KRİPTOGRAFİK HASH ÖNİZLEMESİ
 * ======================================================== */
function initLiveHashPreview() {
    const textInputs = document.querySelectorAll('#text_input');
    textInputs.forEach(textarea => {
        const container = textarea.parentElement.querySelector('.live-hash-container');
        const hashVal = textarea.parentElement.querySelector('#live-hash-val');
        if (!container || !hashVal) return;

        async function updateHash() {
            const val = textarea.value;
            if (val.trim() === '') {
                container.style.display = 'none';
                return;
            }

            try {
                const encoder = new TextEncoder();
                const data = encoder.encode(val);
                const hashBuffer = await crypto.subtle.digest('SHA-256', data);
                const hashArray = Array.from(new Uint8Array(hashBuffer));
                const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                
                hashVal.textContent = hashHex;
                container.style.display = 'block';
            } catch (err) {
                console.error('Crypto API Hata:', err);
            }
        }

        textarea.addEventListener('input', updateHash);
        
        // İlk yüklemede (sayfa doldurulduysa) hemen hesapla
        if (textarea.value.trim() !== '') {
            updateHash();
        }
    });
}

