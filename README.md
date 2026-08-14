# M4 Interior & Architect — Quotation Maker

> A modern quotation management platform for interior designers and architects to create, manage, preview, and download professional quotations.

## Overview

**M4 Interior & Architect Quotation Maker** simplifies the quotation workflow for interior and architectural projects.

The platform provides a centralized dashboard for creating new quotations, managing existing quotations, automatically formatting currency values, previewing quotations as PDFs, downloading PDF documents, and managing profile information.

## Key Features

### Dashboard
- Centralized quotation overview
- Quick access to quotation creation
- Quotation management
- Profile management

### Create New Quotation
Create professional quotations for interior and architectural projects with an organized quotation workflow.

### Automated Currency Formatting
Automatically formats monetary values consistently throughout the quotation, reducing manual formatting and improving presentation.

### PDF Preview
Preview the generated quotation before downloading it to verify project details, items, amounts, currency formatting, and overall presentation.

### Download PDF
Download finalized quotations as professional PDF documents for sharing, printing, or record keeping.

### Manage Quotations
Manage previously created quotations, including viewing quotation details, previewing documents, and downloading PDFs.

### Manage Profile
Manage designer or architect profile information used within the quotation workflow.

## Application Flow

```text
Dashboard
    │
    ├── Create New Quotation
    │       │
    │       ├── Project Details
    │       ├── Quotation Items
    │       ├── Currency Formatting
    │       └── PDF Preview
    │               │
    │               └── Download PDF
    │
    ├── Manage Quotations
    │
    └── Manage Profile
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Database | Neon DB |
| PDF | PDF Preview / PDF Generation |

## Frontend

The application uses **React** with **Vite** for a component-based and fast development experience.

**Tailwind CSS** provides the responsive and modern interface for the dashboard, quotation forms, quotation management screens, and other application components.

## Database

The project uses **Neon DB** for persistent application data.

Quotation-related information can include:

- Profile information
- Client/project details
- Quotation records
- Quotation items
- Pricing
- Totals

> The exact database schema depends on the project implementation.

## Quotation Workflow

```text
Create Quotation
       ↓
Enter Project Details
       ↓
Add Quotation Items
       ↓
Automatic Currency Formatting
       ↓
PDF Preview
       ↓
Review
       ↓
Download PDF
```

## Suggested Project Structure

```text
m4-interior-architect/
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── utils/
│   ├── hooks/
│   ├── assets/
│   └── App.jsx
├── public/
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

> Adjust the structure to match the actual implementation.

## Getting Started

### Prerequisites

- Node.js
- npm
- Git
- Neon DB account/database

### Clone the Repository

```bash
git clone <your-repository-url>
cd m4-interior-architect
```

### Install Dependencies

```bash
npm install
```

### Configure Environment Variables

Create a `.env` file with the environment values required by the project.

Example:

```env
VITE_DATABASE_URL=YOUR_DATABASE_URL
```

Use the actual environment variable names configured in your application.

### Run Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Testing

Important areas include:

- Dashboard navigation
- Quotation creation
- Quotation validation
- Currency formatting
- Quotation calculations
- PDF generation
- PDF preview
- PDF download
- Quotation management
- Profile management
- Responsive layouts
- Database persistence

## Security

For production deployment:

- Keep Neon DB credentials out of source code.
- Use environment variables for sensitive configuration.
- Validate quotation data before persistence.
- Protect user-specific quotation records.
- Never expose database credentials in frontend code.
- Use secure deployment configuration.

## Benefits

M4 Interior & Architect Quotation Maker helps professionals:

- Save time creating quotations.
- Reduce manual formatting.
- Maintain consistent quotation presentation.
- Preview documents before sending.
- Manage quotation records centrally.
- Generate professional PDF documents.
- Keep profile information organized.

## Future Enhancements

- Client management
- Quotation templates
- Custom company branding
- Logo upload
- Multiple currency selection
- Tax and discount calculations
- Quotation status tracking
- Duplicate quotation functionality
- Email quotations to clients
- WhatsApp sharing
- Quotation expiry dates
- Advanced quotation analytics
- Cloud PDF storage
- Invoice generation

## Project Information

**Project:** M4 Interior & Architect  
**Module:** Quotation Maker  
**Type:** Quotation Management Platform  
**Frontend:** React + Vite  
**Database:** Neon DB  
**Styling:** Tailwind CSS

---

⭐ **M4 Interior & Architect — Create. Preview. Manage. Quote Professionally.**
