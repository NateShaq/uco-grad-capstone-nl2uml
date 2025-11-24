import { deflate } from 'pako';
import { encode } from 'plantuml-encoder';

export function encodePlantUML(umlText) {
  return encode(umlText);
}
