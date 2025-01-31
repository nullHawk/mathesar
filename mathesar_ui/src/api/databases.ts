import type { Database } from '@mathesar/AppTypes';
import { getAPI, type PaginatedResponse } from './utils/requestUtils';

function list() {
  return getAPI<PaginatedResponse<Database>>(
    '/api/db/v0/connections/?limit=500',
  );
}

export default {
  list,
};
