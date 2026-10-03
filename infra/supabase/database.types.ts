export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.18"
  }
  public: {
    Tables: {
      account_deletion_requests: {
        Row: {
          completed_at: string | null
          created_at: string
          id: string
          status: string
          user_id: string
        }
        Insert: {
          completed_at?: string | null
          created_at?: string
          id?: string
          status?: string
          user_id: string
        }
        Update: {
          completed_at?: string | null
          created_at?: string
          id?: string
          status?: string
          user_id?: string
        }
        Relationships: []
      }
      admin_users: {
        Row: {
          created_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          user_id?: string
        }
        Relationships: []
      }
      agent_alerts: {
        Row: {
          agent_id: string
          alert_type: string
          created_at: string
          enabled: boolean
          id: string
          user_id: string
        }
        Insert: {
          agent_id: string
          alert_type: string
          created_at?: string
          enabled?: boolean
          id?: string
          user_id: string
        }
        Update: {
          agent_id?: string
          alert_type?: string
          created_at?: string
          enabled?: boolean
          id?: string
          user_id?: string
        }
        Relationships: []
      }
      agent_claims: {
        Row: {
          agent_id: string
          challenge_expires_at: string | null
          challenge_issued_at: string | null
          challenge_token: string | null
          created_at: string
          github_login: string | null
          id: string
          repository: string | null
          status: string
          user_id: string
          verification_method: string
          verification_notes: Json
          verified_at: string | null
        }
        Insert: {
          agent_id: string
          challenge_expires_at?: string | null
          challenge_issued_at?: string | null
          challenge_token?: string | null
          created_at?: string
          github_login?: string | null
          id?: string
          repository?: string | null
          status?: string
          user_id: string
          verification_method?: string
          verification_notes?: Json
          verified_at?: string | null
        }
        Update: {
          agent_id?: string
          challenge_expires_at?: string | null
          challenge_issued_at?: string | null
          challenge_token?: string | null
          created_at?: string
          github_login?: string | null
          id?: string
          repository?: string | null
          status?: string
          user_id?: string
          verification_method?: string
          verification_notes?: Json
          verified_at?: string | null
        }
        Relationships: []
      }
      agent_version_snapshots: {
        Row: {
          agent_id: string
          id: string
          observed_at: string
          source_url: string | null
          version_hash: string
        }
        Insert: {
          agent_id: string
          id?: string
          observed_at?: string
          source_url?: string | null
          version_hash: string
        }
        Update: {
          agent_id?: string
          id?: string
          observed_at?: string
          source_url?: string | null
          version_hash?: string
        }
        Relationships: []
      }
      analytics_events: {
        Row: {
          agent_id: string | null
          event_type: string
          id: string
          metadata: Json
          occurred_at: string
          page_path: string
          referrer: string | null
          session_id: string
          user_id: string | null
        }
        Insert: {
          agent_id?: string | null
          event_type: string
          id?: string
          metadata?: Json
          occurred_at?: string
          page_path?: string
          referrer?: string | null
          session_id: string
          user_id?: string | null
        }
        Update: {
          agent_id?: string | null
          event_type?: string
          id?: string
          metadata?: Json
          occurred_at?: string
          page_path?: string
          referrer?: string | null
          session_id?: string
          user_id?: string | null
        }
        Relationships: []
      }
      claim_audit_events: {
        Row: {
          actor_user_id: string | null
          claim_id: string
          created_at: string
          event_type: string
          id: string
          metadata: Json
        }
        Insert: {
          actor_user_id?: string | null
          claim_id: string
          created_at?: string
          event_type: string
          id?: string
          metadata?: Json
        }
        Update: {
          actor_user_id?: string | null
          claim_id?: string
          created_at?: string
          event_type?: string
          id?: string
          metadata?: Json
        }
        Relationships: [
          {
            foreignKeyName: "claim_audit_events_claim_id_fkey"
            columns: ["claim_id"]
            isOneToOne: false
            referencedRelation: "agent_claims"
            referencedColumns: ["id"]
          },
        ]
      }
      outreach_suppression: {
        Row: {
          contact_key: string
          created_at: string
          reason: string
        }
        Insert: {
          contact_key: string
          created_at?: string
          reason: string
        }
        Update: {
          contact_key?: string
          created_at?: string
          reason?: string
        }
        Relationships: []
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string
          email: string | null
          github_login: string | null
          marketing_opt_in: boolean
          updated_at: string
          user_id: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          email?: string | null
          github_login?: string | null
          marketing_opt_in?: boolean
          updated_at?: string
          user_id: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          email?: string | null
          github_login?: string | null
          marketing_opt_in?: boolean
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      public_agent_index_cache: {
        Row: {
          cache_key: string
          observed_at: string
          payload: Json
          source_url: string
        }
        Insert: {
          cache_key: string
          observed_at?: string
          payload: Json
          source_url: string
        }
        Update: {
          cache_key?: string
          observed_at?: string
          payload?: Json
          source_url?: string
        }
        Relationships: []
      }
      saved_agents: {
        Row: {
          agent_id: string
          created_at: string
          user_id: string
        }
        Insert: {
          agent_id: string
          created_at?: string
          user_id: string
        }
        Update: {
          agent_id?: string
          created_at?: string
          user_id?: string
        }
        Relationships: []
      }
      underwriting_rate_events: {
        Row: {
          agent_id: string | null
          id: string
          occurred_at: string
          task_type: string | null
          user_id: string
        }
        Insert: {
          agent_id?: string | null
          id?: string
          occurred_at?: string
          task_type?: string | null
          user_id: string
        }
        Update: {
          agent_id?: string | null
          id?: string
          occurred_at?: string
          task_type?: string | null
          user_id?: string
        }
        Relationships: []
      }
      user_notifications: {
        Row: {
          agent_id: string
          body: string
          created_at: string
          dedup_key: string
          event_type: string
          id: string
          metadata: Json
          read_at: string | null
          title: string
          user_id: string
        }
        Insert: {
          agent_id: string
          body: string
          created_at?: string
          dedup_key: string
          event_type: string
          id?: string
          metadata?: Json
          read_at?: string | null
          title: string
          user_id: string
        }
        Update: {
          agent_id?: string
          body?: string
          created_at?: string
          dedup_key?: string
          event_type?: string
          id?: string
          metadata?: Json
          read_at?: string | null
          title?: string
          user_id?: string
        }
        Relationships: []
      }
      version_drift_events: {
        Row: {
          agent_id: string
          current_hash: string
          detected_at: string
          id: string
          metadata: Json
          previous_hash: string | null
        }
        Insert: {
          agent_id: string
          current_hash: string
          detected_at?: string
          id?: string
          metadata?: Json
          previous_hash?: string | null
        }
        Update: {
          agent_id?: string
          current_hash?: string
          detected_at?: string
          id?: string
          metadata?: Json
          previous_hash?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      admin_dashboard_metrics: { Args: never; Returns: Json }
      admin_top_agents: {
        Args: { hours_back?: number }
        Returns: {
          agent_id: string
          event_count: number
        }[]
      }
      is_aun_admin: { Args: never; Returns: boolean }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
