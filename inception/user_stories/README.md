# User Stories — GPTFlow

## Epic 1: AI Content Generation

### US-001: Generate Caption
**Sebagai** content creator,
**Saya ingin** memasukkan topik dan mendapatkan caption Instagram yang siap posting,
**Agar** saya tidak perlu menulis dari nol.

**Acceptance Criteria:**
- Input: topik, target audiens, gaya bahasa, jenis konten
- Output: caption + hook + CTA + hashtag (max 30)
- Response time < 10 detik
- Bisa regenerate jika tidak puas

### US-002: Generate Carousel Content
**Sebagai** content creator,
**Saya ingin** mendapatkan judul dan isi per-slide carousel,
**Agar** saya tinggal desain visual tanpa mikir konten.

**Acceptance Criteria:**
- Output: judul carousel + 5-10 slide content + CTA slide terakhir
- Setiap slide max 50 kata
- Edukatif dan engaging

### US-003: Generate Reels Script
**Sebagai** content creator,
**Saya ingin** mendapatkan script pendek untuk reels,
**Agar** saya bisa langsung rekam tanpa scripting manual.

**Acceptance Criteria:**
- Output: hook (3 detik), body (20-50 detik), CTA (5 detik)
- Format: narasi + visual direction
- Durasi total 30-60 detik

### US-004: Generate Story Content
**Sebagai** content creator,
**Saya ingin** mendapatkan ide dan teks untuk Instagram Story,
**Agar** story tetap aktif setiap hari.

**Acceptance Criteria:**
- Output: teks story + poll/quiz suggestion + CTA
- Casual dan engaging tone

## Epic 2: Content Scheduling

### US-005: Schedule Post
**Sebagai** content creator,
**Saya ingin** menjadwalkan konten untuk posting di waktu tertentu,
**Agar** konten terbit konsisten tanpa harus online.

**Acceptance Criteria:**
- Pilih tanggal dan jam posting
- Support timezone WIB
- Bisa reschedule dan cancel

### US-006: Content Calendar
**Sebagai** school manager,
**Saya ingin** melihat kalender konten bulanan,
**Agar** saya tahu planning konten ke depan.

**Acceptance Criteria:**
- View: bulanan dan mingguan
- Color-coded per jenis konten (feed/carousel/reels/story)
- Drag-and-drop reschedule

### US-007: Auto Posting
**Sebagai** system,
**Saya harus** memposting konten yang sudah approved dan terjadwal ke Instagram secara otomatis,
**Agar** tidak ada posting yang terlewat.

**Acceptance Criteria:**
- Posting via Instagram Graph API
- Retry 3x jika gagal
- Notifikasi jika gagal setelah retry

## Epic 3: Approval Workflow

### US-008: Submit for Approval
**Sebagai** content creator,
**Saya ingin** mengirim draft konten untuk di-approve manager,
**Agar** konten sesuai standar sekolah.

**Acceptance Criteria:**
- Status: draft → pending → approved/rejected
- Bisa tambah catatan revisi
- Notifikasi ke approver

### US-009: Approve/Reject Content
**Sebagai** school manager,
**Saya ingin** mereview dan approve/reject konten,
**Agar** hanya konten berkualitas yang terposting.

**Acceptance Criteria:**
- List pending approvals
- Preview konten lengkap
- One-click approve/reject dengan catatan

## Epic 4: Analytics & AI Learning

### US-010: View Engagement Analytics
**Sebagai** school manager,
**Saya ingin** melihat performa setiap posting (likes, comments, reach, saves),
**Agar** saya tahu konten mana yang berhasil.

**Acceptance Criteria:**
- Metrics: likes, comments, shares, saves, reach, impressions
- Trend chart (7d, 30d, 90d)
- Top performing posts

### US-011: AI Recommendation
**Sebagai** content creator,
**Saya ingin** mendapat rekomendasi topik dan format konten dari AI berdasarkan analytics,
**Agar** konten berikutnya lebih baik.

**Acceptance Criteria:**
- AI menganalisis top performing content
- Suggest: topik, format, waktu posting optimal
- Explain reasoning

## Epic 5: Multi-Account & Roles

### US-012: Manage Multiple Instagram Accounts
**Sebagai** admin,
**Saya ingin** mengelola beberapa akun Instagram dari satu dashboard,
**Agar** efisien mengelola berbagai brand/cabang.

**Acceptance Criteria:**
- Add/remove Instagram Business Account
- Switch antar akun
- Per-account analytics

### US-013: Role-Based Access
**Sebagai** admin,
**Saya ingin** mengatur role (admin, manager, creator) per user,
**Agar** akses sesuai tanggung jawab.

**Acceptance Criteria:**
- Roles: admin (full), manager (approve + view), creator (create + schedule)
- Invite user via email
- Revoke access
