/**
 * Dijital İmza Aracı — Tarayıcı Tabanlı Kriptografi Kütüphanesi
 * %100 Client-Side (Zero-Knowledge) Kripto İşlemleri
 */

const CryptoClient = {
    // ArrayBuffer -> Base64 dönüştürücü
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    },

    // Base64 -> ArrayBuffer dönüştürücü
    base64ToArrayBuffer(base64) {
        const binaryString = window.atob(base64.trim());
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    },

    // Veriyi PEM formatına dönüştürücü
    formatToPem(base64Data, label) {
        const lines = [];
        lines.push(`-----BEGIN ${label}-----`);
        for (let i = 0; i < base64Data.length; i += 64) {
            lines.push(base64Data.substring(i, i + 64));
        }
        lines.push(`-----END ${label}-----`);
        return lines.join('\n');
    },

    // PBKDF2 + AES-GCM ile Private Key şifreleme
    async encryptPrivateKey(pkcs8Buffer, password) {
        const encoder = new TextEncoder();
        const passwordBuffer = encoder.encode(password);

        // 16 byte rastgele salt ve 12 byte rastgele IV üret
        const salt = window.crypto.getRandomValues(new Uint8Array(16));
        const iv = window.crypto.getRandomValues(new Uint8Array(12));

        // Şifre üzerinden PBKDF2 anahtarı üret
        const pbkdf2Key = await window.crypto.subtle.importKey(
            "raw",
            passwordBuffer,
            "PBKDF2",
            false,
            ["deriveKey"]
        );

        // AES-256-GCM anahtarını türet (100.000 iterasyon)
        const aesKey = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: salt,
                iterations: 100000,
                hash: "SHA-256"
            },
            pbkdf2Key,
            { name: "AES-GCM", length: 256 },
            false,
            ["encrypt"]
        );

        // PKCS#8 verisini şifrele
        const ciphertextBuffer = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            aesKey,
            pkcs8Buffer
        );

        // Paket yapısı: [16 byte Salt] + [12 byte IV] + [Şifreli Veri + GCM Tag]
        const ciphertextBytes = new Uint8Array(ciphertextBuffer);
        const totalLength = 16 + 12 + ciphertextBytes.length;
        const packageBytes = new Uint8Array(totalLength);
        packageBytes.set(salt, 0);
        packageBytes.set(iv, 16);
        packageBytes.set(ciphertextBytes, 16 + 12);

        const b64 = this.arrayBufferToBase64(packageBytes.buffer);
        return this.formatToPem(b64, "ENCRYPTED PRIVATE KEY");
    },

    // PBKDF2 + AES-GCM ile şifreli Private Key çözme ve yükleme
    async decryptPrivateKey(encryptedPem, password) {
        // PEM başlıklarını ve boşlukları temizle
        const cleanPem = encryptedPem
            .replace(/-----BEGIN ENCRYPTED PRIVATE KEY-----/, "")
            .replace(/-----END ENCRYPTED PRIVATE KEY-----/, "")
            .replace(/\s+/g, "");

        const packageBuffer = this.base64ToArrayBuffer(cleanPem);
        const packageBytes = new Uint8Array(packageBuffer);

        if (packageBytes.length < 16 + 12) {
            throw new Error("Geçersiz veya bozuk özel anahtar dosyası.");
        }

        // Salt, IV ve şifreli veriyi ayır
        const salt = packageBytes.slice(0, 16);
        const iv = packageBytes.slice(16, 16 + 12);
        const ciphertext = packageBytes.slice(16 + 12);

        const encoder = new TextEncoder();
        const passwordBuffer = encoder.encode(password);

        // PBKDF2 anahtarı üret
        const pbkdf2Key = await window.crypto.subtle.importKey(
            "raw",
            passwordBuffer,
            "PBKDF2",
            false,
            ["deriveKey"]
        );

        // AES-256-GCM anahtarını türet
        const aesKey = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: salt,
                iterations: 100000,
                hash: "SHA-256"
            },
            pbkdf2Key,
            { name: "AES-GCM", length: 256 },
            false,
            ["decrypt"]
        );

        // Veriyi çöz
        const decryptedBuffer = await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            aesKey,
            ciphertext
        );

        // Web Crypto API için Private Key nesnesini import et
        // Algoritmayı otomatik tespit etmek için önce RSA-PSS dener, hata alırsa Ed25519'a düşer
        let privateKey;
        try {
            privateKey = await window.crypto.subtle.importKey(
                "pkcs8",
                decryptedBuffer,
                {
                    name: "RSA-PSS",
                    hash: "SHA-256"
                },
                false,
                ["sign"]
            );
        } catch (e) {
            try {
                privateKey = await window.crypto.subtle.importKey(
                    "pkcs8",
                    decryptedBuffer,
                    {
                        name: "Ed25519"
                    },
                    false,
                    ["sign"]
                );
            } catch (e2) {
                throw new Error("Özel anahtar formatı desteklenmiyor veya anahtar bozuk.");
            }
        }

        return privateKey;
    },

    // Tarayıcıda RSA-PSS veya Ed25519 anahtar çifti üretme
    async generateKeyPair(algorithm, keySize, password) {
        let keyPair;
        if (algorithm === "RSA") {
            keyPair = await window.crypto.subtle.generateKey(
                {
                    name: "RSA-PSS",
                    modulusLength: keySize,
                    publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
                    hash: "SHA-256"
                },
                true,
                ["sign", "verify"]
            );
        } else if (algorithm === "Ed25519") {
            keyPair = await window.crypto.subtle.generateKey(
                {
                    name: "Ed25519"
                },
                true,
                ["sign", "verify"]
            );
        } else {
            throw new Error("Geçersiz algoritma seçimi.");
        }

        // Public Key -> SPKI PEM formatına aktar
        const publicBuffer = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
        const publicB64 = this.arrayBufferToBase64(publicBuffer);
        const publicKeyPem = this.formatToPem(publicB64, "PUBLIC KEY");

        // Private Key -> PKCS#8 DER formatına aktar
        const privateBuffer = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey);
        
        // Parola ile şifrele
        const encryptedPrivateKeyPem = await this.encryptPrivateKey(privateBuffer, password);

        return {
            publicKeyPem,
            privateKeyPem: encryptedPrivateKeyPem
        };
    },

    // Veriyi tarayıcıda imzalama
    async signData(privateKey, dataBuffer) {
        let signature;
        if (privateKey.algorithm.name === "RSA-PSS") {
            // Önce SHA-256 Hash hesapla (Sunucu tarafındaki Prehashed RSA-PSS ile tam eşleşme için)
            const hashBuffer = await window.crypto.subtle.digest("SHA-256", dataBuffer);
            signature = await window.crypto.subtle.sign(
                {
                    name: "RSA-PSS",
                    saltLength: 32 // SHA-256 özet uzunluğu kadar salt (32 byte)
                },
                privateKey,
                hashBuffer
            );
        } else if (privateKey.algorithm.name === "Ed25519") {
            // Ed25519 veriyi doğrudan imzalar
            signature = await window.crypto.subtle.sign(
                {
                    name: "Ed25519"
                },
                privateKey,
                dataBuffer
            );
        } else {
            throw new Error("Desteklenmeyen anahtar tipi.");
        }

        return this.arrayBufferToBase64(signature);
    },

    // Verinin SHA-256 hash'ini tarayıcıda hesaplama
    async computeSha256(dataBuffer) {
        const hashBuffer = await window.crypto.subtle.digest("SHA-256", dataBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }
};
