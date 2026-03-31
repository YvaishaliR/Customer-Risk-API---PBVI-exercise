INSERT INTO risk_profiles (customer_id, risk_tier, risk_factors) VALUES
    ('DEMO-001', 'LOW',    ARRAY['Low transaction volume', 'Account age > 5 years', 'No adverse history']),
    ('DEMO-002', 'LOW',    ARRAY['Stable employment verified', 'Low credit utilisation', 'Clean sanctions check']),
    ('DEMO-003', 'LOW',    ARRAY['Single jurisdiction', 'No PEP flag', 'Consistent address history']),
    ('DEMO-004', 'MEDIUM', ARRAY['Moderate transaction velocity', 'Unverified income source']),
    ('DEMO-005', 'MEDIUM', ARRAY['Occasional large cash deposits', 'Business account activity', 'One prior flag resolved']),
    ('DEMO-006', 'MEDIUM', ARRAY['Recently opened account', 'Cross-border transfers present']),
    ('DEMO-007', 'HIGH',   ARRAY['Sanctioned jurisdiction transfer', 'PEP association identified', 'Structuring pattern detected']),
    ('DEMO-008', 'HIGH',   ARRAY['Multiple STRs filed', 'Unresolved adverse media', 'Frequent account changes']),
    ('DEMO-009', 'HIGH',   ARRAY['Dormant account sudden activity', 'High-risk business sector', 'Inconsistent documentation'])
ON CONFLICT (customer_id) DO NOTHING;
