-- 2FA migration

USE fintrack;

-- The TOTP shared secret (base32)
ALTER TABLE users ADD COLUMN totp_secret VARCHAR(64);

-- Master switch.  FALSE until the user confirms a code from their auth app
ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN NOT NULL DEFAULT FALSE;

-- JSON list of one-time recovery codes
ALTER TABLE users ADD COLUMN recovery_codes TEXT;