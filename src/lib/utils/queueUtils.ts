import type { Queue } from '$lib/types';
import { BAG, PIECEVAL, mirrorPieces } from '$lib/constants';

export const queueRegex = new RegExp(`^[${BAG}]+$`);

export function isQueue(s: string): boolean {
  return queueRegex.test(s);
}

export function sortQueue(queue: Queue): Queue {
  const pieces = queue.split('');

  pieces.sort((a, b) => PIECEVAL[a] - PIECEVAL[b]);

  return pieces.join('') as Queue;
}

export function mirrorQueue(queue: Queue): Queue {
  let mirror = '';
  for (const piece of queue) {
    if (piece in mirrorPieces) {
      mirror += mirrorPieces[piece];
    } else {
      mirror += piece;
    }
  }
  return mirror as Queue;
}
