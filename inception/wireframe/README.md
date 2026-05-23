# Wireframe — GPTFlow UI

## Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔵 GPTFlow          [🔔 3] [👤 Admin ▼]          [🌙/☀️]          │
├────────┬────────────────────────────────────────────────────────────┤
│        │                                                            │
│ 📊 Dash│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ ✨ Gen │  │ Posts: 45   │ │ Eng: 4.2%  │ │ Followers   │         │
│ 📅 Cal │  │ this month  │ │ avg rate    │ │ +187 ↑12%   │         │
│ ✓ Appr │  └─────────────┘ └─────────────┘ └─────────────┘         │
│ 📈 Anal│                                                            │
│ ⚙ Set │  ┌─── Upcoming Posts ──────────────────────────────┐       │
│        │  │ 📌 Tips Belajar Efektif    │ Tomorrow 09:00    │       │
│        │  │ 📌 Carousel: Study Hack   │ Wed 18:00         │       │
│        │  │ 📌 Reels: Morning Routine │ Thu 07:00         │       │
│        │  └─────────────────────────────────────────────────┘       │
│        │                                                            │
│        │  ┌─── AI Recommendations ─────────────────────────┐       │
│        │  │ 💡 "Carousel tentang Time Management"          │       │
│        │  │ 💡 "Reels: Behind the scene kelas"             │       │
│        │  │ 💡 "Post jam 18:00 engagement 2x lebih tinggi" │       │
│        │  └─────────────────────────────────────────────────┘       │
└────────┴────────────────────────────────────────────────────────────┘
```

## AI Content Generator

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✨ AI Content Generator                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Topik: [Public Speaking untuk Pemula          ]                    │
│                                                                     │
│  Target Audiens: [Mahasiswa 18-25 tahun        ]                    │
│                                                                     │
│  Gaya Bahasa:  ○ Formal  ● Casual Edukatif  ○ Fun                  │
│                                                                     │
│  Jenis Konten: ○ Feed  ● Carousel  ○ Reels  ○ Story                │
│                                                                     │
│  Konteks Tambahan: [Fokus tips praktis, max 7 slide]                │
│                                                                     │
│  [🤖 Generate Content]   [📋 Use Template ▼]                       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─── Generated Result ─────────────────────────────────────────┐   │
│  │                                                               │   │
│  │  📌 Title: "5 Tips Public Speaking Biar Gak Grogi!"          │   │
│  │                                                               │   │
│  │  🎣 Hook: "90% orang takut ngomong di depan umum..."         │   │
│  │                                                               │   │
│  │  📑 Slides:                                                   │   │
│  │  [1] Kenali Audiensmu                                        │   │
│  │  [2] Latihan di Depan Cermin                                 │   │
│  │  [3] Gunakan Storytelling                                    │   │
│  │  [4] Atur Napas & Postur                                     │   │
│  │  [5] Practice Makes Perfect                                  │   │
│  │                                                               │   │
│  │  📝 Caption: "Pernah grogi pas presentasi?..."               │   │
│  │                                                               │   │
│  │  #️⃣ Hashtags: #publicspeaking #tipskuliah #mahasiswa         │   │
│  │                                                               │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [🔄 Regenerate]  [✏️ Edit]  [💾 Save Draft]  [📤 Submit Approval] │
└─────────────────────────────────────────────────────────────────────┘
```

## Content Calendar

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📅 Content Calendar — Mei 2026        [< Prev] [Next >] [Month|Week]│
├────────┬────────┬────────┬────────┬────────┬────────┬──────────────┤
│  Sen   │  Sel   │  Rab   │  Kam   │  Jum   │  Sab   │  Min        │
├────────┼────────┼────────┼────────┼────────┼────────┼─────────────┤
│   19   │   20   │   21   │   22   │   23   │   24   │   25        │
│🟢Feed  │        │🔵Carou │🟣Reels │🟢Feed  │        │             │
│09:00   │        │18:00   │07:00   │18:00   │        │             │
├────────┼────────┼────────┼────────┼────────┼────────┼─────────────┤
│   26   │   27   │   28   │   29   │   30   │   31   │    1        │
│🟢Feed  │🟡Story │🔵Carou │        │🟢Feed  │🟣Reels │             │
│09:00   │12:00   │18:00   │        │18:00   │07:00   │             │
└────────┴────────┴────────┴────────┴────────┴────────┴─────────────┘

Legend: 🟢 Feed  🔵 Carousel  🟣 Reels  🟡 Story
        ● Posted  ○ Scheduled  ◐ Pending Approval
```

## Approval Queue

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✓ Pending Approvals (3)                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 📌 "Tips Belajar Efektif"                                    │  │
│  │ Type: Feed │ By: Sarah │ Submitted: 2h ago                   │  │
│  │ [👁 Preview]  [✅ Approve]  [❌ Reject]                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 📌 "5 Study Hacks Mahasiswa"                                 │  │
│  │ Type: Carousel │ By: Andi │ Submitted: 5h ago                │  │
│  │ [👁 Preview]  [✅ Approve]  [❌ Reject]                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Design Specs (Implemented v1.0.0-RC)

| Element | Value |
|---------|-------|
| Theme | Dark mode (default) |
| Background | #0f172a |
| Surface/Cards | #1e293b |
| Primary color | #3b82f6 (blue) |
| Warning/Gold | #f59e0b (amber) |
| Success | #10b981 (green) |
| Error | #ef4444 (red) |
| Purple (carousel) | #8b5cf6 |
| Font | Inter, system-ui |
| Border radius | 10px (cards), 6px (buttons) |
| Sidebar width | 220px |
| IG Preview | Dark (#000) mimicking Instagram native |

## Implemented Pages
1. **Auth** — Login/Register (centered card)
2. **Dashboard** — Stats cards + recent content with actions
3. **Generate** — AI form (topic, audience, tone, type) + result preview + image picker
4. **Content** — List with status filter + actions
5. **Calendar** — Monthly grid with color-coded items
6. **Approval** — Pending items with approve/reject
7. **IG Preview Modal** — Instagram-style post preview with:
   - Saved image (Unsplash or uploaded)
   - Carousel slide navigation (◀ ▶)
   - Reels script timeline view
   - Caption, hashtags, action bar
8. **Image Picker** — Unsplash search (4 results) + upload from computer
