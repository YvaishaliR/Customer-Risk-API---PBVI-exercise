DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_tier_enum') THEN
        CREATE TYPE risk_tier_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
    END IF;
END;
$$;

CREATE TABLE IF NOT EXISTS risk_profiles (
    customer_id  VARCHAR(20)    PRIMARY KEY,
    risk_tier    risk_tier_enum NOT NULL,
    risk_factors TEXT[]         NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);
