import RTQView from '@/views/RTQView.vue'
import OverView from '../views/OverView.vue'
import type { RouteRecordRaw } from 'vue-router'
import ExportRecordView from '@/views/ExportRecordView.vue'
import QueryScenarioView from '@/views/QueryScenarioView.vue'
import StandingBookView from '@/views/StandingBookView.vue'
import UserManagementView from '@/views/UserManagementView.vue'
import RoleManagementView from '@/views/RoleManagementView.vue'
import PermManagementView from '@/views/PermManagementView.vue'
import FieldManagementView from '@/views/FieldManagementView.vue'
import FieldCollectView from '@/views/FieldCollectView.vue'
import ModelManagementView from '@/views/ModelManagementView.vue'
import GraphManagementView from '@/views/GraphManagementView.vue'
import AdapterManagementView from '@/views/AdapterManagementView.vue'
import MappingManagementView from '@/views/MappingManagementView.vue'
import PlanManagementView from '@/views/PlanManagementView.vue'
import TaskManagementView from '@/views/TaskManagementView.vue'
import LicenseView from '@/views/LicenseView.vue'
import AboutView from '@/views/AboutView.vue'

export const ROUTES: Record<string, RouteRecordRaw> = {
  overview: {
    path: '/',
    alias: ['/overview'],
    name: 'overview',
    component: OverView,
  },
  real_time_query: {
    path: '/rtq',
    name: 'real_time_query',
    component: RTQView,
  },
  export_record: {
    path: '/export',
    name: 'export_record',
    component: ExportRecordView,
  },
  query_scenario: {
    path: '/qscenario',
    name: 'query_scenario',
    component: QueryScenarioView,
  },
  standing_book: {
    path: '/sbook',
    name: 'standing_book',
    component: StandingBookView,
  },
  user_management: {
    path: '/users',
    name: 'user_management',
    component: UserManagementView,
  },
  role_management: {
    path: '/roles',
    name: 'role_management',
    component: RoleManagementView,
  },
  perm_management: {
    path: '/perms',
    name: 'perm_management',
    component: PermManagementView,
  },
  field_management: {
    path: '/fields',
    name: 'field_management',
    component: FieldManagementView,
  },
  field_collect: {
    path: '/fcollect',
    name: 'field_collect',
    component: FieldCollectView,
  },
  model_management: {
    path: '/models',
    name: 'model_management',
    component: ModelManagementView,
  },
  graph_management: {
    path: '/graphs',
    name: 'graph_management',
    component: GraphManagementView,
  },
  adapter_management: {
    path: '/adapters',
    name: 'adapter_management',
    component: AdapterManagementView,
  },
  mapping_management: {
    path: '/mappings',
    name: 'mapping_management',
    component: MappingManagementView,
  },
  plan_management: {
    path: '/plans',
    name: 'plan_management',
    component: PlanManagementView,
  },
  task_management: {
    path: '/tasks',
    name: 'task_management',
    component: TaskManagementView,
  },
  license: {
    path: '/license',
    name: 'license',
    component: LicenseView,
  },
  about: {
    path: '/about',
    name: 'about',
    component: AboutView,
  },
}
