# Login roles for the AI layer. Passwords are injected from a Kubernetes Secret.
# Grants are defined in 02-schema.sql, after the objects exist.
# The postgres entrypoint sources this file (it is not executable in the ConfigMap),
# so it must not change shell options.

psql -v ON_ERROR_STOP=1 --username postgres --dbname erp \
  -v reader_pw="$AI_READER_PASSWORD" -v writer_pw="$AI_WRITER_PASSWORD" <<'SQL'
CREATE ROLE ai_reader LOGIN PASSWORD :'reader_pw';
CREATE ROLE ai_writer LOGIN PASSWORD :'writer_pw';
SQL
