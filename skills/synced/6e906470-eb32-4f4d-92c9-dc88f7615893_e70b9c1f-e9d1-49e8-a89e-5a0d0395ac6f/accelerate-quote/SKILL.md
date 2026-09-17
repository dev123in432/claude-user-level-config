---
name: accelerate-quote
description: Generate Accelerate Tech branded one-page quotes for client engagements. Use this skill whenever the user asks to create a quote, proposal quote, engagement quote, client quote, one-pager quote, or pricing document for Accelerate Tech. Also trigger when the user says things like "quote for [client]", "price up an engagement", "put together a quote", "generate a quote doc", or references the one-page quote template. This skill handles both Time & Materials and Fixed Price commercial models. Always use this skill for any Accelerate Tech quoting activity — even quick informal requests like "knock up a quote for Camden Council".
---

# Accelerate Tech One-Page Quote Generator

Generate professional, branded one-page quotes using the Accelerate Tech template. The output is a .docx file that matches the company's existing quote format: header metadata, quote details table, charges breakdown, assumptions, and a dual-column signature/acceptance block.

## Workflow

### Step 1: Gather quote information

Collect the following from the user. Accept input either as a conversational interview or as structured data pasted in — both work. If the user gives partial info, ask for what's missing before generating.

**Required fields:**

| Field | Description | Example |
|-------|-------------|---------|
| Quote number | User provides (e.g. OPP-XXXXX-YYYY) | OPP-01136-2025 |
| Quote date | Date the quote is issued | 7 May 2025 |
| Client name | Organisation being quoted | Inner West Council |
| Requested by | Contact name at the client | Steven Thompson |
| Client email | Contact email | steven.thompson@innerwest.nsw.gov.au |
| Quote request name | Short title for the engagement | Nitro Forms Integration Pilot |
| Date required | When the work needs to be completed by | 20 June 2025 |
| Description | 2-4 sentence summary of the proposed work | Free text |
| Commercial model | "Time & Materials" or "Fixed Price" | Time & Materials |
| Line items | One or more: description + amount (AUD ex GST) | See below |
| Assumptions | Bullet points covering scope boundaries | See below |

**Optional fields (have sensible defaults):**

| Field | Default | Notes |
|-------|---------|-------|
| Order number | - (dash) | Client PO number if available |
| Valid until | Quote date + 30 days | Auto-calculated unless overridden |
| Document by | The signer name | Who prepared the doc |
| Signer name | Ask the user | Person signing for Accelerate Tech |
| Signer title | Ask the user | Their role (e.g. CEO, Director) |
| Signer date | Same as quote date | Date of Accelerate Tech signature |
| Date raised | Same as quote date | Usually the same |

**Line items format:**

For **Time & Materials**, each line item typically follows this pattern:
`[X] day(s) - [Role] [Consultant Name] @ $[rate]/day ([breakdown of effort])`

For **Fixed Price**, line items describe deliverables with a fixed amount:
`[Deliverable description]`

Each line item needs a description string and an amount (number). The total is auto-calculated.

**Assumptions** are a list of strings. Common examples include scope boundaries, access requirements, licensing responsibilities, delivery mode (remote/onsite), and dependencies.

### Step 2: Build the JSON config

Once you have all the information, create a JSON config file. Use Australian date format (e.g. "7 May 2025").

```json
{
  "quote_number": "OPP-01136-2025",
  "quote_date": "7 May 2025",
  "order_number": "-",
  "document_by": "James Diekman",
  "client_name": "Inner West Council",
  "requested_by": "Steven Thompson",
  "client_email": "Steven.Thompson@innerwest.nsw.gov.au",
  "valid_until": "6 June 2025",
  "quote_request_name": "Nitro Forms Integration Pilot (Training and Documentation)",
  "date_raised": "7 May 2025",
  "date_required": "20 June 2025",
  "description": "IWC are seeking Accelerate Tech to assist them with...",
  "charges_model": "Time & Material",
  "line_items": [
    {
      "description": "3 day - Senior Consultant [George Demertzis] @ $1,870.00/day (1 day training, 2 days documentation)",
      "amount": 5610.00
    }
  ],
  "assumptions": [
    "Accelerate Tech will perform this engagement remotely.",
    "IWC will provide Accelerate Tech access to Power Automate, Nitro Forms and shared email inboxes.",
    "IWC will procure any required licensing.",
    "This engagement will be conducted in line with the Microsoft funded engagement."
  ],
  "signer_name": "James Diekman",
  "signer_title": "CEO",
  "signer_date": "7 May 2025"
}
```

**Key rules for the config:**
- `charges_model`: Use "Time & Material" or "Fixed Price" — this appears in the charges section header
- `valid_until`: If not provided by the user, calculate as quote_date + 30 calendar days, formatted in Australian date style (e.g. "6 June 2025")
- `amount` in line_items: Always a number (not a string). The script formats it as currency.
- Dollar signs in description strings are fine — the script handles escaping
- `document_by` defaults to the signer name if not specified separately

### Step 3: Generate the document

Save the JSON config, then run the generation script:

```bash
# Copy template to working directory
cp <SKILL_DIR>/assets/template.docx /home/claude/template.docx

# Save config
cat > /home/claude/quote_config.json << 'JSONEOF'
{ ... your config ... }
JSONEOF

# Generate
python <SKILL_DIR>/scripts/generate_quote.py \
  --config /home/claude/quote_config.json \
  --template /home/claude/template.docx \
  --output /mnt/user-data/outputs/quote.docx
```

Replace `<SKILL_DIR>` with the actual path to this skill's directory (the parent of this SKILL.md file).

### Step 4: Deliver

Use `present_files` to share the generated .docx with the user. Keep the summary brief — just confirm the client name, total amount, and validity date.

## Important notes

- **A4 page size**: The template uses A4 (standard Australian business document size)
- **Currency**: All amounts are AUD ex GST. The script formats numbers with comma separators and 2 decimal places
- **Dates**: Use Australian format: "7 May 2025" (day month year, no ordinal suffixes)
- **Signature**: Accelerate Tech's signature uses Lucida Calligraphy italic font for the name. The client side is left blank for them to sign
- **Page break**: The template has a page break before the signature/acceptance section — this is intentional so the quote details and acceptance are on separate pages
- **Header/Footer**: The template includes "Accelerate Tech" header with logo on page 1, and "Commercial in Confidence" footer with page numbers. These are preserved automatically
- **One quote, one file**: Each quote generates a standalone .docx. For revised quotes, generate a new file with an updated quote number or date
