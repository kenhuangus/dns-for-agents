import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_registration.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS agent_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocol TEXT,
            agentName TEXT,
            agentCategory TEXT,
            providerName TEXT,
            version TEXT,
            extension TEXT,
            agentUseJustification TEXT,
            agentCapability TEXT,
            agentEndpoint TEXT,
            agentDID TEXT,
            certificate TEXT,
            csrPEM TEXT,
            a2aAgentCard TEXT,
            mcpClientInformation TEXT,
            agentDNSName TEXT,
            registrationTimestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_registration(agent):
    print(f"[insert_registration] Called with agentName={agent.get('agentName')}")
    print(f"[insert_registration] Using DB_PATH={DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO agent_registrations (
                agentName, agentPolicyId, agentUseJustification, agentCapability, agentEndpoint, agentDID, certificate, csrPEM, a2aAgentCard, mcpClientInformation, agentDNSName, registrationTimestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent.get('agentName'),
            agent.get('agentPolicyId'),
            agent.get('agentUseJustification'),
            agent.get('agentCapability'),
            agent.get('agentEndpoint'),
            agent.get('agentDID'),
            json.dumps(agent.get('certificate', {})),
            agent.get('csrPEM'),
            json.dumps(agent.get('a2aAgentCard', {})),
            json.dumps(agent.get('mcpClientInformation', {})),
            agent.get('agentDNSName'),
            agent.get('registrationTimestamp')
        ))
        conn.commit()
        print("[insert_registration] Insert committed.")
    except Exception as e:
        print(f"[insert_registration] Exception: {e}")
    finally:
        conn.close()


def deactivate_agent(agent_name):
    print(f"[deactivate_agent] Called for agentName={agent_name}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE agent_registrations SET agentStatus='inactive' WHERE agentName=? AND (agentStatus IS NULL OR agentStatus!='inactive')", (agent_name,))
    updated = c.rowcount
    conn.commit()
    conn.close()
    print(f"[deactivate_agent] Updated rows: {updated}")
    return updated > 0

def get_agent_status(agent_name):
    print(f"[get_agent_status] Called for agentName={agent_name}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT agentStatus FROM agent_registrations WHERE agentName=? ORDER BY id DESC LIMIT 1", (agent_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

if __name__ == "__main__":
    init_db()
