import { fail } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { z, type ZodType } from 'zod';

import { queueRegex } from '$lib/utils/queueUtils';
import type { SetupID, Queue } from '$lib/types';

// wrapper to form actions to check schema and coerce types if specified
export function formAction<T, R>(
  schema: ZodType<T>,
  handler: (args: {
    data: T;
    locals: App.Locals;
  }) => R | Promise<R>
) {
  return async ({ request, locals }: RequestEvent) => {
    const formData = await request.formData();

    const returnData = Object.fromEntries(formData);
    const { data, error, success } = schema.safeParse(returnData);

    if (!success) {
      return fail(400, {
        error: z.treeifyError(error)
      });
    }

    return handler({
      data,
      locals
    });
  };
}

// common schema types
export const setupIDSchema = z.string().regex(/^[1-9][0-9a-f]{11}$/).transform(value => value as SetupID)
export const pcSchema = z.coerce.number().int().positive().lte(9);
export const queueSchema = z.string().regex(queueRegex).transform(value => value as Queue);

