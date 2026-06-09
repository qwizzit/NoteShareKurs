import type { InterfaceNoteDto } from "@src/models/InterfaceNoteDto.ts";
import type { InterfaceUserTags } from "@src/models/InterfaceTagDto.ts";

export function findArrayIndexById(array: InterfaceNoteDto[] | InterfaceUserTags[], id: number | null): number {
  if (id === null) {
    return -1;
  }
  return array.findIndex(item => item.id === id);
}