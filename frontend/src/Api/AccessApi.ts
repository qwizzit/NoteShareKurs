import type { InterfaceNoteDto, InterfaceNoteShortDto } from "@src/models/InterfaceNoteDto.ts";
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";
import type { InterfaceTagDto, InterfaceUserTags } from "@src/models/InterfaceTagDto.ts";
import type { InterfaceShortUserDto, InterfaceUserDto } from "@src/models/InterfaceUserDto.ts";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,

  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;

export const AccessApi = {
  setToken(userId: number) {
    localStorage.setItem('token', userId.toString());
    window.location.reload();
  },
  removeToken() {
    localStorage.removeItem("token");
    window.location.reload();
  }
}
export const UsersApi = {
  async getUserId(email: string): Promise<number> {
    return api.get('/users')
      .then(res => res.data.filter((user: InterfaceUserDto) => user.email === email)[0].id);
  },
  async getUser(userId: number): Promise<InterfaceUserDto> {
    return api.get(`/users/${ userId }`)
      .then(res => res.data);
  },
  async getUserSettings(userId: number): Promise<InterfaceSettingsDto> {
    return api.get(`/users/${ userId }/settings`)
      .then(res => res.data);
  }
}
export const NotesApi = {
  async getUserNotes(userId: number): Promise<InterfaceNoteShortDto[]> {
    return api.get(`/notes/user/${ userId }`)
      .then(res => res.data);
  },
  async getUserFullNotes(userId: number): Promise<InterfaceNoteDto[]> {
    return api.get(`/notes/user/${ userId }/full`)
      .then(res => res.data);
  },
  async getNoteData(noteId: number): Promise<{ content: string, tags: InterfaceTagDto[] }> {
    return api.get(`/notes/${ noteId }`)
      .then(res => res.data);
  },
  async getTags(userId: number): Promise<InterfaceUserTags[]> {
    return api.get(`/users/${ userId }/tags`)
      .then(res => res.data);
  },
  async getCollaborators(noteId: number): Promise<{ owner: InterfaceUserDto, collaborators: InterfaceShortUserDto[] }> {
    return api.get(`/notes/${ noteId }/collaborators`)
      .then(res => res.data);
  }
}