"""
Mock data seed script for CommAi MVP.

Creates:
  - 3 sales reps
  - 4 client organizations
  - 4 accounts (one per rep/client pairing)
  - 5 realistic meeting transcripts

Run from the backend/ directory:
    python -m app.data.seed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime
from app.database import SessionLocal, engine, Base
from app import models


TRANSCRIPTS = [
    {
        "title": "Acme Corp — Discovery Call #1",
        "meeting_date": datetime(2025, 6, 2, 10, 0),
        "raw_text": """
[Meeting: Acme Corp Discovery Call — June 2, 2025]
Participants: Sarah Mitchell (Sales Rep, CommAi), David Park (VP Operations, Acme Corp), Linda Torres (IT Director, Acme Corp)

Sarah: Thanks for joining today David, Linda. I'd love to understand what's driving the evaluation right now.

David: Sure. The biggest pain point is our customer service team. We have about 200 agents and they spend roughly 40% of their time just routing tickets and pulling information from five different systems. We need that automated.

Sarah: That's significant. Can you tell me more about the five systems?

Linda: We have Salesforce for CRM, ServiceNow for ticketing, an internal knowledge base on Confluence, a legacy billing system called FinPro, and our product catalog in SAP. Agents have to log into all of them manually.

Sarah: What does the ideal state look like for you?

David: Agents should be able to ask a question in plain English and get a consolidated answer. And for tier-1 issues — password resets, account lookups, that sort of thing — it should just resolve automatically without a human.

Linda: The IT team is also nervous about compliance. We're in financial services. Any AI needs to have audit logs, role-based access control, and ideally on-premise or private cloud deployment.

David: Exactly. We had a bad experience with a vendor last year who couldn't give us data residency guarantees. That's a hard blocker.

Sarah: Understood. What's your timeline looking like?

David: We need something in production by Q4. That gives us about four months. Budget has been approved — we're looking at roughly $500K for the first year.

Linda: We also want to make sure the vendor has professional services support. We don't have the internal AI expertise to do this ourselves.

Sarah: Perfect. That's really helpful context. I'll come back with a proposal focused on agent automation and system integration. 

David: One more thing — our board is asking about ROI metrics. We need to show a reduction in average handle time and deflection rate. Can your solution instrument those?

Sarah: Absolutely, that's built into the reporting layer. We'll make sure that's front and center in the proposal.
""",
    },
    {
        "title": "TechFlow Inc — Requirements Deep Dive",
        "meeting_date": datetime(2025, 6, 5, 14, 0),
        "raw_text": """
[Meeting: TechFlow Inc Requirements Session — June 5, 2025]
Participants: Marcus Reid (Account Executive, CommAi), Priya Sharma (CTO, TechFlow Inc), Jason Kwon (Lead Developer, TechFlow Inc)

Marcus: Great to connect again Priya, Jason. Last time you mentioned wanting to build an internal AI assistant for your engineering team. Let's dig into that today.

Priya: Yes. We have 80 engineers and they're drowning in documentation. Every time someone needs to understand how a microservice works or find the right API, they're pinging the senior engineers on Slack. It's killing productivity.

Jason: We call it the "tribal knowledge problem." The people who built the original systems are leaving and the knowledge isn't captured anywhere useful.

Marcus: What documentation do you currently have?

Jason: We have Confluence wikis, GitHub READMEs, Swagger API specs, and Jira tickets. But nobody searches them because the quality is inconsistent and search is terrible.

Priya: The ask is: can we have an AI that ingests all of that, understands it, and lets engineers ask questions in natural language? Things like "How does the payment processing service handle retries?" or "What's the rate limit on the auth API?"

Marcus: That's a RAG use case — retrieval augmented generation. Yes, absolutely. What would make you choose one vendor over another?

Priya: Two things. First, the model needs to stay within our VPC — we can't have code documentation leaving our network. Second, I want our developers to be able to extend it. It shouldn't be a black box.

Jason: Yeah, we'd want to expose it as an API so teams can build their own tools on top. And we need Slack and VS Code integrations out of the box.

Marcus: What about evaluation? How would you measure success?

Priya: We'd pilot with the payments team. If they can reduce Slack interruptions by 60% in 30 days, we're moving forward with full rollout.

Jason: The other thing — we're a Series B company, cost matters. We don't want to pay per-token pricing that scales unpredictably. We need predictable monthly costs.

Marcus: Completely fair. We can structure that. One question — do you have someone internally who would manage the AI system, or are you looking for us to run it?

Priya: We'd want to own it. Jason's team would manage it. We just need the deployment, initial setup, and training.

Marcus: Got it. I'll put together a technical architecture proposal with pricing options. Can we schedule a follow-up for next week?

Priya: Yes. And please include a section on how the system handles hallucinations — that's a concern I'll need to address with the engineering team.
""",
    },
    {
        "title": "GlobalRetail — AI Strategy Session",
        "meeting_date": datetime(2025, 6, 10, 9, 30),
        "raw_text": """
[Meeting: GlobalRetail AI Strategy Session — June 10, 2025]
Participants: Sarah Mitchell (Sales Rep, CommAi), Robert Chen (Chief Digital Officer, GlobalRetail), Amanda Foster (Head of E-Commerce, GlobalRetail), Kim Nakamura (Head of Supply Chain, GlobalRetail)

Sarah: Thank you all for making time. I know this is a broad group which tells me the scope is significant. Robert, where would you like to start?

Robert: We have three separate initiatives that we think AI can address, and frankly I want to see if one platform can handle all three rather than buying three point solutions.

Sarah: That makes sense. Walk me through them.

Robert: First is personalization. Our website has 8 million SKUs and our recommendation engine is outdated. We're losing revenue because customers can't find what they want. Amanda can speak to that.

Amanda: Right now our recommendations are rule-based. Bought X, show Y. Our conversion rate is 1.2% — industry average is 3.5%. We need AI-driven recommendations that factor in browsing behavior, purchase history, seasonal trends, and inventory levels.

Sarah: And what's the urgency on that one?

Amanda: We're heading into holiday season in Q3 prep. If we don't have something by August we miss the window.

Kim: My initiative is different — supply chain intelligence. We have 3,000 suppliers and we're constantly getting surprised by stockouts. I want AI to predict demand and flag at-risk suppliers before it becomes a problem.

Sarah: What data sources feed into that?

Kim: ERP data from SAP, supplier portals, weather data, shipping carrier APIs, and our point-of-sale data. Currently no one system sees all of that together.

Sarah: Got it. And the third initiative, Robert?

Robert: Internal operations — AI for our store managers. They manage teams of 50-100 people and are buried in scheduling, HR queries, compliance training reminders. We want an AI assistant that handles the administrative layer so managers can focus on the floor.

Sarah: That's three distinct but connected use cases. What does your current AI infrastructure look like?

Robert: We're on Azure. We have a small data science team — six people. They're good but they're at capacity.

Amanda: I need to flag a dependency. Our recommendation system touches our website, mobile app, and in-store kiosks. Any solution needs to integrate with our existing Adobe Commerce setup.

Kim: And for supply chain, I need to be able to explain the AI's decisions to our procurement team. They won't trust a black box.

Robert: Budget is the other thing. We have $2M approved but the CFO wants to see ROI on at least two of the three use cases within 12 months. Can you speak to typical implementation timelines and returns?

Sarah: I can, and I have case studies that directly parallel each of your scenarios. Let me put together a phased proposal — personalization first since that has the tightest deadline, then supply chain, then internal operations. Sound right?

Robert: That works. I'd also want to see your model governance story. We had a PR issue last year with a recommendation showing inappropriate content. That cannot happen again.

Sarah: Content safety and governance is built in at the platform level — I'll make sure that's prominent in the proposal.
""",
    },
    {
        "title": "HealthBridge — Compliance and Automation Review",
        "meeting_date": datetime(2025, 6, 12, 11, 0),
        "raw_text": """
[Meeting: HealthBridge Requirements Review — June 12, 2025]
Participants: Marcus Reid (Account Executive, CommAi), Dr. Susan Okafor (CMIO, HealthBridge), Tom Walters (VP IT & Security, HealthBridge), Rachel Simmons (Director of Clinical Operations)

Marcus: Thanks for having me. HealthBridge is doing impressive work — 12 hospitals and growing. Let's talk about where AI fits for you.

Dr. Okafor: We have two priority areas. The first is clinical documentation. Our physicians are spending 3 hours per day on documentation. It's a burnout crisis. We need AI that can listen to a patient encounter, generate a draft clinical note, and push it into Epic for the physician to review and approve.

Marcus: That's ambient documentation — we have experience here. What are the hard requirements?

Tom: HIPAA compliance is non-negotiable. All PHI — protected health information — must stay within our Azure Government cloud environment. No data can leave that boundary. Full stop.

Dr. Okafor: The clinical accuracy bar is very high. We can use AI to draft but a physician must always approve before anything enters the medical record. The liability exposure otherwise is too great.

Rachel: The workflows also have to match how physicians actually work. If it adds friction, they won't adopt it. We've had three failed EHR projects because the IT team designed them without clinical input.

Marcus: That's a critical point. Do you have a clinical informatics team we'd work with?

Dr. Okafor: Yes, I lead it. Six physician champions across specialties. They would be involved in the pilot design.

Tom: Security-wise, we need SOC 2 Type II, HITRUST certification, and a Business Associate Agreement from day one — not after the sale.

Marcus: Understood. What's the second priority area?

Dr. Okafor: Prior authorization. We have 1,200 prior auth requests per day. Sixty percent of them are denials that get appealed and eventually approved. That means 720 cases per day where a human is essentially doing unnecessary work. We want AI to pre-screen the request, pull the relevant clinical data from the EHR, and auto-approve the clear-cut cases.

Rachel: That alone would save us an estimated $4.2 million per year in administrative costs. We have the data to prove it.

Marcus: That's compelling. What does the current state look like technically?

Tom: Epic EHR, Azure Government, and a mix of legacy systems for billing and insurance. The prior auth process currently runs through a combination of Epic and a standalone tool called Olive.

Marcus: Timeline?

Dr. Okafor: Ambient documentation pilot — we want to start in September with 20 physicians in our cardiology department. Prior auth is a longer runway, probably a full year given the integration complexity.

Tom: One more thing. We've had vendors promise HIPAA compliance and then deliver something that's technically compliant but operationally unworkable. I need references from other health systems you've deployed in.

Marcus: I'll get you three health system references this week. Same size and complexity as HealthBridge.
""",
    },
    {
        "title": "Acme Corp — Follow-up: Technical Architecture Review",
        "meeting_date": datetime(2025, 6, 18, 10, 0),
        "raw_text": """
[Meeting: Acme Corp Technical Architecture Follow-up — June 18, 2025]
Participants: Sarah Mitchell (Sales Rep, CommAi), James Carter (Solutions Architect, CommAi), David Park (VP Operations, Acme Corp), Linda Torres (IT Director, Acme Corp), Wei Zhang (Enterprise Architect, Acme Corp)

Sarah: Thanks everyone for joining. James is our solutions architect and he's going to walk through the proposed architecture.

James: Thanks Sarah. So based on the discovery call, I've put together a reference architecture for Acme's customer service automation platform. Let me walk through the key components.

Wei: Before you start — what's the deployment model? Our CISO needs on-prem or private cloud. Public SaaS is a non-starter.

James: Fully understood. What we're proposing is a private cloud deployment on your existing Azure tenant. All compute, storage, and model inference happens within your subscription. Nothing touches our infrastructure.

Linda: What about the model itself? Where does inference run?

James: Within your Azure environment. We deploy the model weights to your Azure Machine Learning workspace. You own the compute, you control the access.

Wei: And the integrations to Salesforce, ServiceNow, Confluence, FinPro, and SAP?

James: Each integration is a connector deployed as a function app in your Azure environment. They authenticate using OAuth or API keys managed in Azure Key Vault. No credentials leave your tenant.

David: What's the latency like? Customer service agents can't be waiting 10 seconds for a response.

James: The P95 latency target is under 2 seconds for information retrieval queries. For automated resolution — the tier-1 flows — it's 5-8 seconds including back-end system transactions.

Linda: We have a peak load of about 500 concurrent agents during business hours. Can the architecture handle that?

James: Yes, we'd scale the inference endpoint to handle 1,000 concurrent requests — double your peak. The auto-scaling is managed by Azure ML.

Wei: I have concerns about the knowledge base freshness. Our product catalog in SAP changes daily. If the AI is answering questions based on stale data, we'll have a problem.

James: Good callout. We'd configure a nightly incremental sync from SAP and Confluence. For Salesforce and ServiceNow we can do near-real-time via webhooks — changes propagate within 60 seconds.

David: What does the rollout look like?

James: Three phases. Phase 1 — 4 weeks — is the knowledge base build and Salesforce/ServiceNow integration. Phase 2 — 6 weeks — adds the legacy integrations and the tier-1 automation flows. Phase 3 — 4 weeks — is UAT, load testing, and go-live.

David: 14 weeks. That's tight for Q4 but doable. What can go wrong?

James: The highest risk is the FinPro legacy integration. It doesn't have a modern API — we'd need to build a screen-scraping connector or work with the FinPro vendor to expose an endpoint. Do you have a relationship there?

Linda: Yes, we have a support contract. I can reach out to their technical team this week.

Sarah: Let's capture that as a next step. Linda, can you send us the FinPro technical contact by end of week?

Linda: Will do.

David: One thing we haven't discussed — what happens if the AI gives a wrong answer to a customer?

James: There are two safeguards. First, every answer includes a confidence score. If it's below 80%, the system routes to a human agent automatically. Second, all responses are logged with the source citations so you can audit exactly why the AI said what it said.

Wei: I like that. The audit trail is something our compliance team has been asking for.

David: I think we're close. What's the contracting timeline?

Sarah: If you're ready to proceed, I can have a contract to you by end of this week. We'd need a signed agreement to hold the Q4 implementation slots.

David: Let's plan for that. Linda, Wei — any blockers?

Linda: Not from IT. We need the FinPro connection resolved but that's a parallel track.

Wei: No blockers. I'm satisfied with the architecture. Let's move.
""",
    },
]


def seed():
    db = SessionLocal()
    try:
        # ── Sales Reps ────────────────────────────────────────────────────────
        rep1 = models.SalesRep(name="Sarah Mitchell", email="sarah.mitchell@commai.io", territory="Enterprise East")
        rep2 = models.SalesRep(name="Marcus Reid", email="marcus.reid@commai.io", territory="Enterprise West")
        db.add_all([rep1, rep2])
        db.flush()

        # ── Clients ───────────────────────────────────────────────────────────
        acme = models.Client(company_name="Acme Corp", industry="Financial Services", website="https://acmecorp.example.com")
        techflow = models.Client(company_name="TechFlow Inc", industry="Software / SaaS", website="https://techflow.example.com")
        globalretail = models.Client(company_name="GlobalRetail", industry="Retail", website="https://globalretail.example.com")
        healthbridge = models.Client(company_name="HealthBridge", industry="Healthcare", website="https://healthbridge.example.com")
        db.add_all([acme, techflow, globalretail, healthbridge])
        db.flush()

        # ── Accounts ──────────────────────────────────────────────────────────
        acme_account = models.Account(
            sales_rep_id=rep1.id,
            client_id=acme.id,
            account_name="Acme Corp — Customer Service Automation",
            stage="proposal",
            notes="High-value deal. Q4 target. Privacy/compliance requirements. FinPro integration risk.",
        )
        techflow_account = models.Account(
            sales_rep_id=rep2.id,
            client_id=techflow.id,
            account_name="TechFlow — Engineering Knowledge Assistant",
            stage="discovery",
            notes="RAG use case. VPC requirement. Predictable pricing critical.",
        )
        globalretail_account = models.Account(
            sales_rep_id=rep1.id,
            client_id=globalretail.id,
            account_name="GlobalRetail — AI Platform (3 initiatives)",
            stage="discovery",
            notes="Large multi-initiative deal. Personalization deadline is August.",
        )
        healthbridge_account = models.Account(
            sales_rep_id=rep2.id,
            client_id=healthbridge.id,
            account_name="HealthBridge — Ambient Documentation & Prior Auth",
            stage="discovery",
            notes="HIPAA / HITRUST required. Azure Government. Epic integration.",
        )
        db.add_all([acme_account, techflow_account, globalretail_account, healthbridge_account])
        db.flush()

        # ── Transcripts ───────────────────────────────────────────────────────
        account_map = {
            0: (acme_account, rep1),
            1: (techflow_account, rep2),
            2: (globalretail_account, rep1),
            3: (healthbridge_account, rep2),
            4: (acme_account, rep1),
        }

        for i, t_data in enumerate(TRANSCRIPTS):
            account, rep = account_map[i]
            transcript = models.Transcript(
                account_id=account.id,
                sales_rep_id=rep.id,
                title=t_data["title"],
                meeting_date=t_data["meeting_date"],
                raw_text=t_data["raw_text"].strip(),
                status=models.TranscriptStatus.pending,
            )
            db.add(transcript)

        db.commit()
        print("✅ Mock data seeded successfully.")
        print(f"   • 2 sales reps")
        print(f"   • 4 clients")
        print(f"   • 4 accounts")
        print(f"   • {len(TRANSCRIPTS)} transcripts")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Seeding mock data...")
    seed()
