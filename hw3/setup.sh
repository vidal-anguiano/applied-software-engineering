#! bin/bash

createdb bigbus -U postgres
psql -U postgres -d bigbus -f dbschema.sql
