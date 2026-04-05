-- =====================================================
-- DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM SCHEMA
-- =====================================================

-- RESULTS TABLE (NEW - CRITICAL REQUIREMENT)
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    polling_station_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- FOREIGN KEY CONSTRAINTS
    FOREIGN KEY (polling_station_id) REFERENCES pollingstation(id),
    FOREIGN KEY (candidate_id) REFERENCES candidate(id),
    
    -- VALIDATION CONSTRAINTS
    CHECK (votes >= 0),
    
    -- PREVENT DUPLICATE ENTRIES
    UNIQUE(polling_station_id, candidate_id)
);

-- RESULT AGGREGATION CACHE TABLE (PERFORMANCE OPTIMIZATION)
CREATE TABLE IF NOT EXISTS aggregated_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    area_type VARCHAR(20) NOT NULL, -- 'county', 'constituency', 'ward'
    area_id INTEGER NOT NULL,
    total_votes INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (candidate_id) REFERENCES candidate(id),
    FOREIGN KEY (position_id) REFERENCES position(id),
    
    UNIQUE(candidate_id, position_id, area_type, area_id)
);

-- VOTING SESSIONS TABLE (FOR ELECTION MANAGEMENT)
CREATE TABLE IF NOT EXISTS voting_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RESULTS BACKUP TABLE (FOR AUDIT TRAIL)
CREATE TABLE IF NOT EXISTS results_backup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    polling_station_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    votes INTEGER NOT NULL,
    action_type VARCHAR(20) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    performed_by VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (result_id) REFERENCES results(id),
    FOREIGN KEY (polling_station_id) REFERENCES pollingstation(id),
    FOREIGN KEY (candidate_id) REFERENCES candidate(id)
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_results_polling_station ON results(polling_station_id);
CREATE INDEX IF NOT EXISTS idx_results_candidate ON results(candidate_id);
CREATE INDEX IF NOT EXISTS idx_results_votes ON results(votes);
CREATE INDEX IF NOT EXISTS idx_aggregated_results_lookup ON aggregated_results(candidate_id, position_id, area_type, area_id);
CREATE INDEX IF NOT EXISTS idx_results_backup_timestamp ON results_backup(timestamp);

-- TRIGGERS FOR AUTOMATIC AGGREGATION
CREATE TRIGGER IF NOT EXISTS update_aggregated_results
AFTER INSERT OR UPDATE OR DELETE ON results
BEGIN
    -- This trigger would be implemented in application logic for better control
    -- SQLite triggers are limited, so we'll handle aggregation in Django
    NULL;
END;

-- VIEWS FOR EASY DATA ACCESS
CREATE VIEW IF NOT EXISTS v_mca_results AS
SELECT 
    c.id as candidate_id,
    c.first_name,
    c.last_name,
    c.party_id,
    p.name as party_name,
    w.id as ward_id,
    w.name as ward_name,
    const.id as constituency_id,
    const.name as constituency_name,
    county.id as county_id,
    county.name as county_name,
    COALESCE(SUM(r.votes), 0) as total_votes
FROM candidate c
JOIN position pos ON c.position_id = pos.id
JOIN party p ON c.party_id = p.id
JOIN ward w ON c.ward_id = w.id
JOIN constituency const ON w.constituency_id = const.id
JOIN county county ON const.county_id = county.id
LEFT JOIN results r ON c.id = r.candidate_id
WHERE pos.name = 'MCA'
GROUP BY c.id, c.first_name, c.last_name, c.party_id, p.name, w.id, w.name, const.id, const.name, county.id, county.name;

CREATE VIEW IF NOT EXISTS v_mp_results AS
SELECT 
    c.id as candidate_id,
    c.first_name,
    c.last_name,
    c.party_id,
    p.name as party_name,
    const.id as constituency_id,
    const.name as constituency_name,
    county.id as county_id,
    county.name as county_name,
    COALESCE(SUM(r.votes), 0) as total_votes
FROM candidate c
JOIN position pos ON c.position_id = pos.id
JOIN party p ON c.party_id = p.id
JOIN constituency const ON c.constituency_id = const.id
JOIN county county ON const.county_id = county.id
LEFT JOIN polling_station ps ON const.id = ps.constituency_id
LEFT JOIN results r ON c.id = r.candidate_id AND ps.id = r.polling_station_id
WHERE pos.name = 'MP'
GROUP BY c.id, c.first_name, c.last_name, c.party_id, p.name, const.id, const.name, county.id, county.name;

CREATE VIEW IF NOT EXISTS v_county_results AS
SELECT 
    c.id as candidate_id,
    c.first_name,
    c.last_name,
    c.party_id,
    p.name as party_name,
    pos.name as position_name,
    county.id as county_id,
    county.name as county_name,
    COALESCE(SUM(r.votes), 0) as total_votes
FROM candidate c
JOIN position pos ON c.position_id = pos.id
JOIN party p ON c.party_id = p.id
JOIN county county ON c.county_id = county.id
LEFT JOIN polling_station ps ON county.id = ps.county_id
LEFT JOIN results r ON c.id = r.candidate_id AND ps.id = r.polling_station_id
WHERE pos.name IN ('Governor', 'Senator', 'WOMEN_REP')
GROUP BY c.id, c.first_name, c.last_name, c.party_id, p.name, pos.name, county.id, county.name;
